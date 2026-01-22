'use client';

import { useRef, useState, useEffect } from 'react';
import Board from '../ui/Board';
import { GameData, GameState } from '@/app/game/model';
import { formatBudget } from '../ui/lib/utils';
import { moveWithDice, nextTurn } from '@/app/game/data';
import FunctionalityScreen from './FunctionalityScreen';
interface GameScreenProps {
  selectedCamera: string;
  gameState: GameState;
  gameData: GameData;
  onBack: () => void;
  onGameStateUpdate: (newGameState: GameState) => void;
}

interface DetectionResult {
  bboxes: number[][];
  scores: number[];
}

function CameraCapture({ selectedCamera, onCapture }: { selectedCamera: string; onCapture: (imageData: string, result: DetectionResult) => void }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const startCamera = async () => {
      try {
        const mediaStream = await navigator.mediaDevices.getUserMedia({
          video: selectedCamera ? { deviceId: { exact: selectedCamera } } : true
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
    <div className="flex flex-col items-center">
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

function DetectionResult({ imageData, result, onBack, onConfirm }: { imageData: string; result: DetectionResult; onBack: () => void; onConfirm: (dice1: number, dice2: number) => void }) {
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
        <button
          onClick={() => onConfirm(result.scores[0], result.scores[1])}
          className="px-4 py-2 border-2 bg-green-600 rounded text-center text-sm font-bold text-white hover:bg-green-700"
        >
          Xác nhận: {result.scores.join(' ')}
        </button>
        <button
          onClick={onBack}
          className="px-4 py-2 bg-yellow-600 text-white rounded hover:bg-yellow-700 font-bold"
        >
          Chụp lại
        </button>
      </div>
    </div>
  );
}

export default function GameScreen({ selectedCamera, gameState, gameData, onBack, onGameStateUpdate }: GameScreenProps) {
  const [capturedImage, setCapturedImage] = useState<string | null>(null);
  const [detectionResult, setDetectionResult] = useState<DetectionResult | null>(null);
  const [showCameraPopup, setShowCameraPopup] = useState(false);
  const [showBoardPopup, setShowBoardPopup] = useState(false);
  const [isMoving, setIsMoving] = useState(false);
  // const [intermediateStates, setIntermediateStates] = useState<GameState[]>([]);
  // const [currentStateIndex, setCurrentStateIndex] = useState(0);
  const [showEndTurnButton, setShowEndTurnButton] = useState(false);
  const [showRollAgainButton, setShowRollAgainButton] = useState(false);
  const [isFunctionDisabled, setIsFunctionDisabled] = useState(false);
  const [movementLines, setMovementLines] = useState<{ from: string, to: string, isLast: boolean }[]>([]);
  const [showFunctionalityScreen, setShowFunctionalityScreen] = useState(false);
  const [boardMessage, setBoardMessage] = useState<string>('');
  
  // Functionality screen persistent state
  const [functionalityTab, setFunctionalityTab] = useState<'main' | 'dev'>('main');
  const [devDice1, setDevDice1] = useState(1);
  const [devDice2, setDevDice2] = useState(1);

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

  const handleConfirmDice = async (dice1: number, dice2: number) => {
    try {
      // Call the move_with_dice API
      const response = await moveWithDice({
        game_state: gameState,
        dice1,
        dice2
      });

      // Store intermediate states
      // setIntermediateStates(response.intermediate_states);
      // setCurrentStateIndex(0);
      setIsMoving(true);

      // Close the popup
      setShowCameraPopup(false);
      handleBackToCamera();

      // Disable "chức năng" button and hide "Thảy" button
      setIsFunctionDisabled(true);

      // Start the animation
      startMovementAnimation(response.intermediate_states);

    } catch (error) {
      console.error('Error confirming dice:', error);
    }
  };

  const startMovementAnimation = (states: GameState[]) => {
    let index = 0;
    const lines: { from: string, to: string, isLast: boolean }[] = [];
    let accumulatedMessages: string[] = [];

    const moveToNextState = () => {
      if (index < states.length) {
        const currentState = states[index];
        
        // Update the game state to the current intermediate state
        onGameStateUpdate(currentState);
        
        // Process pending actions for this state during animation
        if (currentState.pending_actions && currentState.pending_actions.length > 0) {
          // Extract all show_message actions
          const messageActions = currentState.pending_actions.filter(action => action.type === 'show_message');
          messageActions.forEach(action => {
            if (action.data.message && !accumulatedMessages.includes(action.data.message)) {
              accumulatedMessages.push(action.data.message);
            }
          });
          
          // Update board message with all accumulated messages
          if (accumulatedMessages.length > 0) {
            setBoardMessage(accumulatedMessages.join('\n'));
          }
        }

        // Build movement lines from consecutive states
        if (index > 0) {
          const currentPlayer = states[0].current_player;
          const fromPos = states[index - 1].players[currentPlayer].at;
          const toPos = states[index].players[currentPlayer].at;
          const isLast = index === states.length - 1;

          lines.push({ from: fromPos, to: toPos, isLast });
          setMovementLines([...lines]);
        }

        index++;
        setTimeout(moveToNextState, 100);
      } else {
        // Animation finished, check pending actions for turn control
        setIsMoving(false);
        setIsFunctionDisabled(false); // Re-enable "Chức năng" button after movement
        
        const finalState = states[states.length - 1];
        const endTurnAction = finalState.pending_actions?.find(a => a.type === 'end_turn');
        
        if (endTurnAction) {
          // Always show "Kết thúc lượt" button regardless of doubles
          setShowEndTurnButton(true);
          setShowRollAgainButton(false);
        }
      }
    };
    moveToNextState();
  };

  const handleEndTurn = async () => {
    try {
      // Call next_turn API
      const response = await nextTurn({
        game_state: gameState
      });

      // Update game state with new current player
      onGameStateUpdate(response.new_game_state);

      // Reset UI state
      setShowEndTurnButton(false);
      setShowRollAgainButton(false);
      setMovementLines([]); // Clear movement lines
      setBoardMessage(''); // Clear board message

    } catch (error) {
      console.error('Error ending turn:', error);
    }
  };

  // Game board grid
  const cols1 = [2, 3, 3, 3, 3, 3, 3, 2, 4, 2];
  const cols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'R', 'U'];

  // Get players from gameState
  const players = gameState?.players ? Object.entries(gameState.players).map(([playerId, playerData]: [string, any]) => {
    return {
      color: playerId,
      budget: playerData.budget,
      at: playerData.at
    };
  }) : [];

  const current_player_color = gameData.color_pallete.players[gameState.current_player];
  
  // Check if roll button should be shown (same logic as in the game screen)
  const canRoll = !showEndTurnButton && !isMoving;
  
  // Show functionality screen if requested
  if (showFunctionalityScreen) {
    return (
      <FunctionalityScreen
        onBack={() => setShowFunctionalityScreen(false)}
        onExit={onBack}
        onDevRoll={async (dice1, dice2) => {
          setShowFunctionalityScreen(false);
          await handleConfirmDice(dice1, dice2);
        }}
        activeTab={functionalityTab}
        setActiveTab={setFunctionalityTab}
        devDice1={devDice1}
        setDevDice1={setDevDice1}
        devDice2={devDice2}
        setDevDice2={setDevDice2}
        canRoll={canRoll}
      />
    );
  }
  
  return (
    <div className="flex h-screen p-1 bg-[#2E6C3D]">
      {/* Left Panel */}
      <div className="left-sidebar flex flex-col pr-4">

        {/*Game Board */}
        <div
          className="bds-wrapper border-2 border-white p-1 rounded flex-1 cursor-pointer transition-colors"
          onClick={() => setShowBoardPopup(true)}
        >
          <div className="flex gap-1 h-full">
            {/* Columns */}
            {cols.map((col, colIndex) => (
              <div key={col} className="flex-1 flex flex-col gap-1 justify-end">
                {/* Cells for this column */}
                {Array.from({ length: cols1[colIndex] }, (_, rowIndex) => (
                  <div
                    key={`${col}${rowIndex + 1}`}
                    style={{ backgroundColor: '#FF8B8B', color: "black", fontSize: '20px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '400', textAlign: 'center' }}
                    className="bds-node border aspect-square"
                  >3</div>
                ))}
                {/* Column header at bottom */}
                <div className="b-col text-center text-sm font-bold items-center justify-center text-white">
                  {col}
                </div>
              </div>
            ))}
          </div>
        </div>
        {/* Player Colors */}
        <div className="text-white border-2 border-white p-2 rounded bg-gray-700 min-h-[48vh]">
          <div className="flex flex-col h-full gap-1">
            {players.map((player, _) => (
              <div
                key={player.color}
                className="flex items-center gap-1 max-h-[5vh]"
              >
                <div
                  className={`border-2 border-white flex items-center justify-center h-full w-[10%]`}
                  style={{
                    backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 5px, rgba(0,0,0,0.2) 5px, rgba(0,0,0,0.2) 10px)',
                    backgroundColor: gameData.color_pallete.players[player.color]
                  }}
                />
                <span className="font-bold text-gray-100 text-sm">{formatBudget(player.budget)}</span>
                <span className="font-bold text-gray-300 text-sm">• {formatBudget(player.budget)}</span>
              </div>
            ))}
              <div
                key="house"
                className="flex items-center gap-1 max-h-[6vh]"
              >
                <div
                  className={`border-2 border-white flex items-center justify-center h-full w-[10%]`}
                  style={{
                    backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 5px, rgba(0,0,0,0.2) 5px, rgba(0,0,0,0.2) 10px)',
                    backgroundColor: "gray"
                  }}
                />
                <span className="font-bold text-sm text-gray-100">{`32 • 12`}</span>
              </div>
          </div>
        </div>

        {/* Function Button */}
        <button
          onClick={() => setShowFunctionalityScreen(true)}
          disabled={isFunctionDisabled}
          className="border-2 border-white w-full text-lg font-bold py-1 rounded text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ backgroundColor: current_player_color }}
        >Chức năng</button>
      </div>
      <Board
        gameData={gameData}
        gameState={gameState}
        movementLines={movementLines}
        message={boardMessage}
      />
      {/* Right Panel - Empty with button to open camera */}
      <div className="txx-button w-1/2 flex flex-col items-center justify-center">
        {showEndTurnButton ? (
          <button
            onClick={handleEndTurn}
            className="px-4 py-6 text-lg text-gray-600 font-bold rounded border-3 border-gray-500"
            style={{ backgroundColor: current_player_color }}
          >
            Kết thúc lượt
          </button>
        ) : gameState.pending_actions?.some(a => a.type === 'roll_dice') && !isMoving && (
          <button
            onClick={() => {
              setBoardMessage('');
              setMovementLines([]);
              setShowCameraPopup(true);
            }}
            className="px-4 py-6 text-lg text-gray-600 font-bold rounded border-3 border-gray-500"
            style={{ backgroundColor: current_player_color }}
          >
            Thảy
          </button>
        )}
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
                onConfirm={handleConfirmDice}
              />
            ) : (
              <CameraCapture selectedCamera={selectedCamera} onCapture={handleCapture} />
            )}
          </div>
        </div>
      )}

      {/* Board Popup */}
      {showBoardPopup && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
          <div className="bg-gray-900 rounded-lg p-6 max-w-4xl w-full mx-4" style={{ maxHeight: '90vh' }}>
            <div className="flex justify-between items-center mb-4">
              <button
                onClick={() => setShowBoardPopup(false)}
                className="close-popup text-4xl text-white hover:text-red-500"
              >
                ×
              </button>
            </div>
            <div className="bg-gray-800 p-4 rounded" style={{ height: '70vh' }}>
              <div className="flex gap-2 h-full">
                {/* Columns */}
                {cols.map((col, colIndex) => (
                  <div key={col} className="flex-1 flex flex-col gap-2 justify-end">
                    {/* Cells for this column */}
                    {Array.from({ length: cols1[colIndex] }, (_, rowIndex) => (
                      <div
                        key={`${col}${rowIndex + 1}`}
                        style={{ color: 'orange', fontSize: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '900' }}
                        className="border-2 bg-white aspect-square rounded"
                      >1</div>
                    ))}
                    {/* Column header at bottom */}
                    <div className="text-center text-2xl font-bold items-center justify-center text-white">
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
