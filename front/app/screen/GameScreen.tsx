'use client';

import { ColorType } from '@/app/utils/ColorType';
import { useRef, useState, useEffect } from 'react';

interface GameScreenProps {
  selectedColors: ColorType[];
  selectedCamera: string;
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
    <div className="flex flex-col items-center space-y-4">
      <div className="flex flex-1 border-2 border-gray-300 rounded p-4 bg-gray-50 justify-center h-[60vh]">
        <div className="flex">
          <video ref={videoRef} autoPlay playsInline muted className="rounded" />
        </div>
      </div>
      <button
        onClick={captureImage}
        className="px-4 py-2 bg-blue-500 text-white rounded"
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
      <div className="flex flex-1 border-2 border-gray-300 rounded p-4 bg-gray-50 justify-center">
        <div className="flex h-[60vh]">
          <canvas ref={canvasRef} className="rounded" />
        </div>
      </div>
      <div className="flex gap-2">
        <div className="px-4 py-2 border rounded text-center text-sm m-0">{result.scores.join(' ')}</div>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-gray-500 text-white rounded"
        >
          Chụp lại
        </button>
      </div>
    </div>
  );
}

export default function GameScreen({ onBack }: GameScreenProps) {
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(null);

  const handleCapture = (imageData: string, result: DetectionResult) => {
    setCapturedImage(imageData);
    setDetectionResult(result);
  };

  const handleBackToCamera = () => {
    setCapturedImage(null);
    setDetectionResult(null);
  };

  return (
    <div className="flex flex-col items-center justify-center h-full p-4">
      <button
        onClick={onBack}
        className="absolute top-4 left-4 text-2xl font-bold text-gray-600 hover:text-gray-800 rounded hover:bg-gray-100 bg-blue-200 p-2"
      >
        ↩
      </button>
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
  );
}
