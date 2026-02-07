import { useEffect } from 'react';
import { GameBoardProps } from './props';

export function GameCamera(props: GameBoardProps) {
  const { videoRef, selectedCamera, stream, setStream } = props;

  useEffect(() => {
    const startCamera = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: selectedCamera ?
            { deviceId: { exact: selectedCamera } } :
            true
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
  }, [selectedCamera]);

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted
      className="w-full h-full object-contain"
    />
  );
}
