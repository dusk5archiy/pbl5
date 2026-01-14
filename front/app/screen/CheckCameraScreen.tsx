'use client';

import { useRef, useEffect, useState, Dispatch, SetStateAction } from 'react';

interface CheckCameraScreenProps {
  selectedCamera: string;
  setSelectedCamera: Dispatch<SetStateAction<string>>;
  onBack: () => void;
  onContinue: () => void;
}

interface CameraSelectProps {
  cameras: MediaDeviceInfo[];
  selectedCamera: string;
  onCameraChange: (deviceId: string) => void;
}

function CameraSelect({ cameras, selectedCamera, onCameraChange }: CameraSelectProps) {
  return (
    <div className="flex flex-col overflow-auto border border-gray-500 rounded w-[30vw] whitespace-nowrap">
      {cameras.map((camera) => (
        <div
          key={camera.deviceId}
          onClick={() => onCameraChange(camera.deviceId)}
          className={`px-2 py-1 text-xs ${selectedCamera === camera.deviceId
            ? 'text-blue-800 font-bold'
            : 'text-gray-700'
            }`}
        >
          {camera.label || `Camera ${camera.deviceId.slice(0, 8)}...`}
        </div>
      ))}
    </div>
  );
}

interface CameraViewProps {
  videoRef: React.RefObject<HTMLVideoElement | null>;
}

function CameraView({ videoRef }: CameraViewProps) {
  return (
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
  );
}

export default function CheckCameraScreen({ selectedCamera, setSelectedCamera, onBack, onContinue }: CheckCameraScreenProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [cameras, setCameras] = useState<MediaDeviceInfo[]>([]);

  useEffect(() => {
    const setupCamera = async () => {
      try {
        // Stop current stream if it exists
        if (streamRef.current) {
          streamRef.current.getTracks().forEach(track => track.stop());
        }

        // Request camera access - use selected camera if available, otherwise default
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: selectedCamera ? { deviceId: { exact: selectedCamera } } : true
        });

        // After permission granted, enumerate available cameras (only on first load)
        if (cameras.length === 0) {
          const devices = await navigator.mediaDevices.enumerateDevices();
          const videoDevices = devices.filter(device => device.kind === 'videoinput');
          setCameras(videoDevices);

          // Set default camera if none selected
          if (videoDevices.length > 0 && !selectedCamera) {
            setSelectedCamera(videoDevices[0].deviceId);
          }
        }

        streamRef.current = mediaStream;
        if (videoRef.current) {
          videoRef.current.srcObject = mediaStream;
        }
      } catch (error) {
        // Browser will handle permission prompt and errors
      }
    };

    setupCamera();

    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
        streamRef.current = null;
      }
    };
  }, [selectedCamera, setSelectedCamera, cameras.length]);

  const refreshCameras = async () => {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      const videoDevices = devices.filter(device => device.kind === 'videoinput');
      setCameras(videoDevices);
    } catch (error) {
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
            <CameraSelect
              cameras={cameras}
              selectedCamera={selectedCamera}
              onCameraChange={setSelectedCamera}
            />
            <CameraView videoRef={videoRef} />
          </div>

          <div className="flex justify-center gap-4 mt-4">
            <button              onClick={refreshCameras}
              className="px-4 py-2 border-4 border-blue-500 rounded-lg font-bold bg-blue-100 text-gray-800 hover:bg-blue-200"
            >
              Làm mới
            </button>
            <button              onClick={onContinue}
              className="px-4 py-2 border-4 border-green-500 rounded-lg font-bold bg-green-100 text-gray-800"
            >
              Tiếp tục
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
