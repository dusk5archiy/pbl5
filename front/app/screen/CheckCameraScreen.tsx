'use client';

import { useRef, useEffect, useState } from 'react';

interface CheckCameraScreenProps {
  onBack: () => void;
  onContinue: () => void;
}

export default function CheckCameraScreen({ onBack, onContinue }: CheckCameraScreenProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: { facingMode: 'user' }
        });
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

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current;
      const video = videoRef.current;
      const context = canvas.getContext('2d');

      if (context) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageDataUrl = canvas.toDataURL('image/png');
        setCapturedImage(imageDataUrl);
      }
    }
  };

  const handleContinue = () => {
    if (capturedImage) {
      onContinue();
    }
  };

  return (
    <div className="flex flex-col gap-4 h-screen bg-gray-100">
      <div className="flex flex-col m-4 grow gap-6">
        <div className="border-4 border-green-500 h-full rounded px-[4vw] py-[6vh] bg-white">

          <div className="flex items-center gap-4 h-[10vh] mb-2">
            <button
              onClick={onBack}
              className="aspect-square h-full text-2xl font-bold text-gray-600 hover:text-gray-800 rounded hover:bg-gray-100 bg-blue-200"
            >
              ↩
            </button>
            <h2 className="font-bold">Thiết lập camera</h2>
          </div>

          <div className="flex gap-4 h-[40vh]">
            {/* Camera View Window */}
            <div className="flex flex-1 border-2 border-gray-300 rounded p-4 bg-gray-50 justify-center">
              <div className="flex">
                <video
                  ref={videoRef}
                  autoPlay
                  playsInline
                  muted
                  className="rounded"
                />
              </div>
            </div>

            {/* Captured Image Window */}
            <div className="flex flex-1 border-2 border-gray-300 rounded-lg p-4 bg-gray-50 justify-center">
              {capturedImage ? (
                <div className="flex">
                  <img
                    src={capturedImage}
                    alt="Captured"
                    className="rounded"
                  />
                </div>
              ) : (
                <div className="flex flex-1 border-2 border-gray-300 rounded-lg p-4 bg-gray-50"></div>
              )}
            </div>
          </div>

          <canvas ref={canvasRef} className="hidden" />

          <div className="flex justify-center gap-4 mt-4">
            <button
              onClick={captureImage}
              className="px-4 py-1 bg-blue-500 text-white font-bold rounded-lg"
            >
              Chụp ảnh
            </button>
            <button
              onClick={handleContinue}
              disabled={!capturedImage}
              className={`px-6 py-3 font-bold rounded-lg ${capturedImage
                ? 'bg-green-500 text-white'
                : 'bg-gray-300 text-gray-500'
                }`}
            >
              Tiếp tục
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
