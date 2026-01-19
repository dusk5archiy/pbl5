'use client';

import { ColorType } from '@/app/utils/ColorType';
import { useRef, useState, useEffect } from 'react';
import Board from '../ui/Board';
interface GameScreenProps {
  selectedColors: ColorType[];
  selectedCamera: string;
  gameState: any;
  onBack: () => void;
}

interface DetectionResult {
  bboxes: number[][];
  scores: number[];
}

function CameraCapture({ onCapture }: { onCapture: (imageData: string, result: DetectionResult) => void }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true });
        setStream(mediaStream);
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      } catch (error) {
        console.error('Error accessing camera:', error);
      }
    };

    startCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const captureImage = async () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.drawImage(video, 0, 0);
        canvas.toBlob(async (blob) => {
          if (blob) {
            await sendImage(blob);
          }
        });
      }
    }
  };

  const sendImage = async (blob: Blob) => {
    setLoading(true);
    const formData = new FormData();
    formData.append('file', blob, 'capture.jpg');

    try {
      const response = await fetch('http://localhost:8000/detect', {
        method: 'POST',
        body: formData,
      });
      const data: DetectionResult = await response.json();
      const imageData = canvasRef.current!.toDataURL();
      onCapture(imageData, data);
    } catch (error) {
      console.error('Error sending image:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center ">
      <div className="flex flex-1 border-4 border-green-500 rounded bg-gray-800 justify-center">
        <div className="flex">
          <video ref={videoRef} autoPlay playsInline muted className="camera rounded max-h-96" />
        </div>
      </div>
      <button
        onClick={captureImage}
        className="px-2 py-1 bg-green-600 text-white text-lg font-bold rounded hover:bg-green-700"
        disabled={loading}
      >
        {loading ? 'Đang xử lí...' : 'Chụp xúc xắc'}
      </button>
      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}

function DetectionResult({ imageData, result, onBack }: { imageData: string; result: DetectionResult; onBack: () => void }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (canvasRef.current && imageData) {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        const img = new Image();
        img.onload = () => {
          canvas.width = img.width;
          canvas.height = img.height;
          ctx.drawImage(img, 0, 0);

          // Draw bounding boxes and scores
          ctx.strokeStyle = 'red';
          ctx.lineWidth = 2;
          ctx.fillStyle = 'red';
          ctx.font = '20px Arial';
          result.bboxes.forEach((bbox, index) => {
            const [x, y, w, h] = bbox;
            ctx.strokeRect(x, y, w, h);
            ctx.fillText(result.scores[index].toString(), x, y - 5);
          });
        };
        img.src = imageData;
      }
    }
  }, [imageData, result]);

  return (
    <div className="flex flex-col items-center space-y-2">
      <div className="flex flex-1 border-4 border-green-500 rounded p-4 bg-gray-800 justify-center">
        <div className="flex">
          <canvas ref={canvasRef} className="camera rounded max-h-96" />
        </div>
      </div>
      <div className="flex gap-2">
        <div className="px-4 py-2 border-2 border-green-500 rounded text-center text-lg font-bold">{result.scores.join(' ')}</div>
        <button
          onClick={onBack}
          className="px-6 py-3 bg-yellow-600 text-white rounded hover:bg-yellow-700 font-bold"
        >
          Chụp lại
        </button>
      </div>
    </div>
  );
}

export default function GameScreen({ selectedColors, gameState, onBack }: GameScreenProps) {
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(null);
  const [showCameraPopup, setShowCameraPopup] = useState(false);
  const [showBoardPopup, setShowBoardPopup] = useState(false);

  useEffect(() => {
    if (gameState) {
      console.log('Game state received:', gameState);
    }
  }, [gameState]);

  const handleCapture = (imageData: string, result: DetectionResult) => {
    setCapturedImage(imageData);
    setDetectionResult(result);
  };

  const handleBackToCamera = () => {
    setCapturedImage(null);
    setDetectionResult(null);
  };

  const handleCloseCameraPopup = () => {
    setShowCameraPopup(false);
    handleBackToCamera();
  };

  // Game board grid
  const cols1 = [2, 3, 3, 3, 3, 3, 3, 2, 4, 2];
  const cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'R', 'U'];

  return (
    <div className="flex h-screen text-white p-1">
      {/* Left Panel */}
      <div className="left-sidebar flex flex-col  pr-4">
        {/* Player Colors */}
        <div className="money-wrapper border-2 border-white p-2 rounded" style={{ height: '260px' }}>
          <div className="flex flex-col h-full justify-between">
            {selectedColors.map((color, index) => (
              <div 
                key={index} 
                className="flex items-center space-x-2"
                style={{ height: `${260 / selectedColors.length}px` }}
              >
                <div
                  className={`${color.bgClass} border-2 border-white flex items-center justify-center`}
                  style={{
                    width: `${Math.max(220 / selectedColors.length , 32)}px`,
                    height: `${Math.max(220 / selectedColors.length , 32)}px`,
                    backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 5px, rgba(0,0,0,0.2) 5px, rgba(0,0,0,0.2) 10px)'
                  }}
                />
                <span className="font-bold" style={{ fontSize: `${Math.max(260 / selectedColors.length / 2.5, 20)}px` }}>1.5M</span>
              </div>
            ))}
          </div>
        </div>

        {/* Game Board */}
        <div 
          className="bds-wrapper border-2 border-white p-1 rounded flex-1 cursor-pointer hover:border-green-500 transition-colors"
          onClick={() => setShowBoardPopup(true)}
        >
          <div className="flex gap-1 h-full">
            {/* Columns */}
            {cols.map((col, colIndex) => (
              <div key={col} className="flex-1 flex flex-col gap-1 justify-end">
                {/* Cells for this column */}
                {Array.from({ length: cols1[colIndex] }, (_, rowIndex) => (
                  <div
                    key={`${col}${rowIndex+1}`}
                    style={{color:'orange', fontSize:'13px', display:'flex', alignItems:'center', justifyContent:'center', fontWeight:'900'}}
                    className="border bg-white aspect-square"
                  >1</div>
                ))}
                {/* Column header at bottom */}
                <div className="b-col text-center text-sm font-bold items-center justify-center">
                  {col}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Pause Button */}
        <div className="func-btn border-2 border-white p-2 rounded">
          <button
            onClick={onBack}
            className="w-full text-xl font-bold py-2 rounded"
          >
            chức năng
          </button>
        </div>
      </div>
            <Board/>
      {/* Right Panel - Empty with button to open camera */}
      <div className="txx-button w-1/2 flex flex-col items-center justify-center">
        <button
          onClick={() => setShowCameraPopup(true)}
          className="px-2 py-2 bg-green-600 text-white text-xl font-bold rounded hover:bg-green-700"
        >
          Chụp xúc xắc
        </button>
      </div>

      {/* Camera Popup */}
      {showCameraPopup && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="xx-popup bg-gray-900 border-4 border-green-500 rounded-lg p-4 max-w-3xl mx-3">
            <div className="flex justify-between items-center mb-2">
              <h2 className="text-2xl font-bold text-green-400">Thảy xúc xắc</h2>
              <button
                onClick={handleCloseCameraPopup}
                className="text-3xl text-white hover:text-red-500"
              >
                ×
              </button>
            </div>
            {capturedImage && detectionResult ? (
              <DetectionResult
                imageData={capturedImage}
                result={detectionResult}
                onBack={handleBackToCamera}
              />
            ) : (
              <CameraCapture onCapture={handleCapture} />
            )}
          </div>
        </div>
      )}

      {/* Board Popup */}
      {showBoardPopup && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
          <div className="bg-gray-900 rounded-lg p-6 max-w-4xl w-full mx-4" style={{ maxHeight: '90vh' }}>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-3xl font-bold text-blue-400">Bảng trò chơi</h2>
              <button
                onClick={() => setShowBoardPopup(false)}
                className="text-4xl text-white hover:text-red-500"
              >
                ×
              </button>
            </div>
            <div className="bg-gray-800 border-2 border-white p-4 rounded" style={{ height: '70vh' }}>
              <div className="flex gap-2 h-full">
                {/* Columns */}
                {cols.map((col, colIndex) => (
                  <div key={col} className="flex-1 flex flex-col gap-2 justify-end">
                    {/* Cells for this column */}
                    {Array.from({ length: cols1[colIndex] }, (_, rowIndex) => (
                      <div
                        key={`${col}${rowIndex+1}`}
                        style={{color:'orange', fontSize:'24px', display:'flex', alignItems:'center', justifyContent:'center', fontWeight:'900'}}
                        className="border-2 bg-white aspect-square rounded"
                      >1</div>
                    ))}
                    {/* Column header at bottom */}
                    <div className="text-center text-2xl font-bold items-center justify-center">
                      {col}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
