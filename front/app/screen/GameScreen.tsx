'use client';

import { useRef, useState, useEffect } from 'react';
import Board from '../ui/Board';
import PropertyBoard from '../ui/PropertyBoard';
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

function CameraInBoard({ selectedCamera }: { selectedCamera: string }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);

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

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted
      className="amber-box-camera w-full h-full object-contain"
    />
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
    <div className="w-full h-full flex flex-col items-center gap-4 justify-center">
      <div className="flex border-4 border-green-500 rounded p-1 bg-gray-800 justify-center h-[70%] w-[90%] overflow-hidden,">
        <div className="w-full h-full flex items-center justify-center overflow-hidden">
          <canvas ref={canvasRef} className="max-w-full max-h-full object-contain camera rounded" />
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
  const [showBoardPopup, setShowBoardPopup] = useState(false);
  const [isMoving, setIsMoving] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showConfirmationPopup, setShowConfirmationPopup] = useState(false);
  // const [intermediateStates, setIntermediateStates] = useState<GameState[]>([]);
  // const [currentStateIndex, setCurrentStateIndex] = useState(0);
  const [showEndTurnButton, setShowEndTurnButton] = useState(false);
  const [isFunctionDisabled, setIsFunctionDisabled] = useState(false);
  const [movementLines, setMovementLines] = useState<{ from: string, to: string, isLast: boolean }[]>([]);
  const [showFunctionalityScreen, setShowFunctionalityScreen] = useState(false);
  const [boardMessage, setBoardMessage] = useState<string>('');

  // Functionality screen persistent state
  const [functionalityTab, setFunctionalityTab] = useState<'main' | 'dev'>('main');
  const [devDice1, setDevDice1] = useState(1);
  const [devDice2, setDevDice2] = useState(1);


  const handleBackToCamera = () => {
    setCapturedImage(null);
    setDetectionResult(null);
    setShowConfirmationPopup(false);
  };

  const handleCaptureFromAmberBox = async () => {
    const videoElement = document.querySelector('.amber-box-camera') as HTMLVideoElement;
    const canvas = document.createElement('canvas');

    if (videoElement) {
      canvas.width = videoElement.videoWidth;
      canvas.height = videoElement.videoHeight;
      const ctx = canvas.getContext('2d');

      if (ctx) {
        setIsAnalyzing(true);
        ctx.drawImage(videoElement, 0, 0);

        canvas.toBlob(async (blob) => {
          if (blob) {
            const formData = new FormData();
            formData.append('file', blob, 'capture.jpg');

            try {
              const response = await fetch('http://localhost:8000/detect', {
                method: 'POST',
                body: formData,
              });
              const data: DetectionResult = await response.json();
              const imageData = canvas.toDataURL();
              setCapturedImage(imageData);
              setDetectionResult(data);
              setShowConfirmationPopup(true);
            } catch (error) {
              console.error('Error analyzing image:', error);
            } finally {
              setIsAnalyzing(false);
            }
          }
        });
      }
    }
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

      // Close the popups
      setShowConfirmationPopup(false);
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
      setMovementLines([]); // Clear movement lines
      setBoardMessage(''); // Clear board message

    } catch (error) {
      console.error('Error ending turn:', error);
    }
  };

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

  const isRollDiceButtonActive = gameState.pending_actions?.some(a => a.type === 'roll_dice');

  return (
    <div className="flex h-screen p-1 bg-[#2E6C3D] gap-1">
      {/* Left Panel */}
      <div className="flex flex-col w-[40vw] gap-1 overflow-hidden">
        {/*Game Board */}
        <div
          className="flex gap-1 border-2 border-white p-1 rounded h-[25%] bg-[#446655] items-center"
          onClick={() => setShowBoardPopup(true)}
        >
          <PropertyBoard
            key={`property-board-${movementLines.length}`}
            gameData={gameData}
            gameState={gameState}
            showBorders={movementLines.length > 0}
          />
        </div>
        <div className="flex flex-1 gap-1">
          <div className='flex flex-col gap-1 w-[70%] h-full'>
            <div className="flex flex-col border-2 border-white p-[2vh] rounded bg-gray-700 h-[70%]">
              <div className="flex flex-col gap-[1vh] overflow-hidden">
                {gameState?.players && Object.entries(gameState.players).map(([playerId, playerData]: [string, any]) => (
                  <div
                    key={playerId}
                    className="flex items-center gap-1 max-h-[5vh]"
                  >
                    <div
                      className="border-2 border-white flex items-center justify-center h-full w-[10%] min-w-2"
                      style={{
                        backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 5px, rgba(0,0,0,0.2) 5px, rgba(0,0,0,0.2) 10px)',
                        backgroundColor: gameData.color_pallete.players[playerId]
                      }}
                    />
                    <span className="font-bold text-gray-100 text-[5vh]">{formatBudget(playerData.budget)}</span>
                    <span className="font-bold text-gray-300 text-[5vh] whitespace-nowrap">• {formatBudget(playerData.total)}</span>
                  </div>
                ))}
                <div
                  key="house"
                  className="flex items-center gap-1 max-h-[6vh]"
                >
                  <div
                    className={`border-2 border-white flex items-center justify-center h-full w-[10%] min-w-2`}
                    style={{
                      backgroundImage: 'repeating-linear-gradient(45deg, transparent, transparent 5px, rgba(0,0,0,0.2) 5px, rgba(0,0,0,0.2) 10px)',
                      backgroundColor: "gray"
                    }}
                  />
                  <span className="font-bold text-[5vh] text-gray-100 whitespace-nowrap">{`32 • 12`}</span>
                </div>
              </div>
            </div>
            <button
              onClick={handleEndTurn}
              className="flex-1 text-[5vh] font-bold rounded border-2 border-gray-500 disabled:text-white"
              style={{ backgroundColor: current_player_color }}
              disabled={!showEndTurnButton}
            >
              Kết thúc lượt
            </button>
          </div>
          <div className='flex flex-col flex-1 gap-1'>
            <div className='flex flex-col h-[70%] gap-1'>
              <button
                onClick={() => {
                  setBoardMessage('');
                  setMovementLines([]);
                  handleCaptureFromAmberBox();
                }}
                className="w-full h-[50%] text-[5vh] text-gray-600 font-bold rounded border-3 border-gray-500 disabled:text-white"
                disabled={!isRollDiceButtonActive || isAnalyzing}
                style={{ backgroundColor: current_player_color }}
              >
                Thảy
              </button>
              <button
                onClick={() => setShowFunctionalityScreen(true)}
                disabled={isFunctionDisabled}
                className="w-full h-[50%] border-2 text-[3vh] border-gray-600 font-bold py-1 rounded text-gray-700 disabled:text-white bg-white"
              >Chức năng
              </button>
            </div>
            <button
              onClick={() => {
                setBoardMessage('');
                setMovementLines([]);
              }}
              className="w-full flex-1 text-[5vh] text-gray-600 font-bold rounded border-3 border-gray-500 disabled:text-white"
              disabled
              style={{ backgroundColor: current_player_color }}
            >
              Tiếp
            </button>
          </div>
        </div>

        {/* Function Button */}
      </div>
      <div className='relative'>
        <Board
          gameData={gameData}
          gameState={gameState}
          movementLines={movementLines}
          message={boardMessage}
        />
        {/* Amber Box with Camera */}
        <div className="w-1/2 flex flex-col items-center justify-center overflow-hidden"
          style={
            {
              position: "absolute",
              top: `${4 / 13 * 100}%`,
              left: `${2 / 13 * 100}%`,
              width: `${(13 - 4) / 13 * 100}%`,
              height: `${(13 - 7) / 13 * 100}%`,
            }
          }
        >
          <CameraInBoard selectedCamera={selectedCamera} />
        </div>
      </div>

      {/* Confirmation Popup */}
      {showConfirmationPopup && capturedImage && detectionResult && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="flex bg-gray-900 border-4 border-green-500 rounded-lg p-4 h-[90vh] w-[70vw] justify-center items-center">
            <DetectionResult
              imageData={capturedImage}
              result={detectionResult}
              onBack={handleBackToCamera}
              onConfirm={handleConfirmDice}
            />
          </div>
        </div>
      )}

      {/* Board Popup */}
      {/* {showBoardPopup && ( */}
      {/*   <div className="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50"> */}
      {/*     <div className="bg-gray-900 rounded-lg p-6 max-w-4xl w-full mx-4" style={{ maxHeight: '90vh' }}> */}
      {/*       <div className="flex justify-between items-center mb-4"> */}
      {/*         <button */}
      {/*           onClick={() => setShowBoardPopup(false)} */}
      {/*           className="close-popup text-4xl text-white hover:text-red-500" */}
      {/*         > */}
      {/*           × */}
      {/*         </button> */}
      {/*       </div> */}
      {/*       <div className="bg-gray-800 p-4 rounded" style={{ height: '70vh' }}> */}
      {/*         <div className="flex gap-2 h-full"> */}
      {/*           {cols.map((col, colIndex) => ( */}
      {/*             <div key={col} className="flex-1 flex flex-col gap-2 justify-end"> */}
      {/*               {Array.from({ length: cols1[colIndex] }, (_, rowIndex) => ( */}
      {/*                 <div */}
      {/*                   key={`${col}${rowIndex + 1}`} */}
      {/*                   style={{ color: 'orange', fontSize: '24px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '900' }} */}
      {/*                   className="border-2 bg-white aspect-square rounded" */}
      {/*                 >1</div> */}
      {/*               ))} */}
      {/*               <div className="text-center text-2xl font-bold items-center justify-center text-white"> */}
      {/*                 {col} */}
      {/*               </div> */}
      {/*             </div> */}
      {/*           ))} */}
      {/*         </div> */}
      {/*       </div> */}
      {/*     </div> */}
      {/*   </div> */}
      {/* )} */}
    </div>
  );
}
