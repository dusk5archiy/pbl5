'use client';

import { useRef, useState, useEffect } from 'react';
import Board from '../ui/Board';
import BDSTab from '../ui/BDSTab';
import LeftPanel from '../ui/LeftPanel';
import TitleDeed from '../ui/TitleDeed';
import { GameData, GameState } from '@/app/game/model';
import { formatBudget } from '../ui/lib/utils';
import { moveWithDice, nextTurn, buyProperty, payRent, payJailFine, payTax } from '@/app/game/data';
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
  const [isMoving, setIsMoving] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showConfirmationPopup, setShowConfirmationPopup] = useState(false);
  const [showEndTurnButton, setShowEndTurnButton] = useState(false);
  const [isFunctionDisabled, setIsFunctionDisabled] = useState(false);
  const [movementLines, setMovementLines] = useState<{ from: string, to: string, isLast: boolean }[]>([]);
  const [showFunctionalityScreen, setShowFunctionalityScreen] = useState(false);
  const [boardMessage, setBoardMessage] = useState<string>('');
  const [showBuyPropertyPopup, setShowBuyPropertyPopup] = useState(false);
  const [buyPropertyData, setBuyPropertyData] = useState<{ property_id: string; price: number; buyable: boolean } | null>(null);
  const [showPayRentPopup, setShowPayRentPopup] = useState(false);
  const [payRentData, setPayRentData] = useState<{ property_id: string; owner: string; rent: number } | null>(null);
  const [isInDebtMode, setIsInDebtMode] = useState(false);
  const [showPayJailPopup, setShowPayJailPopup] = useState(false);
  const [forcedJailDice, setForcedJailDice] = useState<{ dice1: number; dice2: number } | null>(null);
  const [showPayTaxPopup, setShowPayTaxPopup] = useState(false);
  const [payTaxData, setPayTaxData] = useState<{ tax_type: string; amount: number } | null>(null);
  const [functionalityTab, setFunctionalityTab] = useState<'main' | 'dev'>('main');
  const [devDice1, setDevDice1] = useState(1);
  const [devDice2, setDevDice2] = useState(1);
  const [showBDSTab, setShowBDSTab] = useState(false);
  const [selectedPropertyId, setSelectedPropertyId] = useState<string | null>(null);


  const handleBackToCamera = () => {
    setCapturedImage(null);
    setDetectionResult(null);
    setShowConfirmationPopup(false);
    setIsFunctionDisabled(false);
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
        setIsFunctionDisabled(true);
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
              setIsFunctionDisabled(true);
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
          const prevState = states[index - 1];
          const currentState = states[index];
          const fromPos = prevState.players[currentPlayer].at;
          const toPos = currentState.players[currentPlayer].at;
          let isLast = index === states.length - 1;

          // Don't draw line if jumping to OT (jail position) - this happens when going to jail
          const jumpingToJail = toPos === "OT" && currentState.players[currentPlayer].in_jail;
          
          // Check if next state is jumping to jail - if so, mark current line as last
          if (index < states.length - 1) {
            const nextState = states[index + 1];
            const nextPos = nextState.players[currentPlayer].at;
            const nextIsJumpToJail = nextPos === "OT" && nextState.players[currentPlayer].in_jail;
            if (nextIsJumpToJail) {
              isLast = true; // Draw arrow head at current position (VT)
            }
          }
          
          if (!jumpingToJail && fromPos !== toPos) {
            lines.push({ from: fromPos, to: toPos, isLast });
            setMovementLines([...lines]);
          }
        }

        index++;
        setTimeout(moveToNextState, 100);
      } else {
        // Animation finished, wait 500ms before processing final state
        setTimeout(() => {
          setIsMoving(false);
          setIsFunctionDisabled(false);

          const finalState = states[states.length - 1];
          const currentPlayer = finalState.current_player;
          const finalPosition = finalState.players[currentPlayer].at;

          // Set selected property if player landed on a BDS
          if (finalPosition in gameData.bds) {
            setSelectedPropertyId(finalPosition);
          }

          // Check for buy_property action
          const buyPropertyAction = finalState.pending_actions?.find(a => a.type === 'buy_property');
          if (buyPropertyAction) {
            setBuyPropertyData({
              property_id: buyPropertyAction.data.property_id,
              price: buyPropertyAction.data.price,
              buyable: buyPropertyAction.data.buyable
            });
            setShowBuyPropertyPopup(true);
            setIsFunctionDisabled(true);
          }

          // Check for pay_rent action
          const payRentAction = finalState.pending_actions?.find(a => a.type === 'pay_rent');
          if (payRentAction) {
            setPayRentData({
              property_id: payRentAction.data.property_id,
              owner: payRentAction.data.owner,
              rent: payRentAction.data.rent
            });
            setShowPayRentPopup(true);
            setIsFunctionDisabled(true);
          }

          // Check for forced jail payment action
          const forcedJailPaymentAction = finalState.pending_actions?.find(a => a.type === 'pay_jail_fine_forced');
          if (forcedJailPaymentAction) {
            setForcedJailDice({
              dice1: forcedJailPaymentAction.data.dice1,
              dice2: forcedJailPaymentAction.data.dice2
            });
            setShowPayJailPopup(true);
            setIsFunctionDisabled(true);
          }

          // Check for pay_tax action
          const payTaxAction = finalState.pending_actions?.find(a => a.type === 'pay_tax');
          if (payTaxAction) {
            setPayTaxData({
              tax_type: payTaxAction.data.tax_type,
              amount: payTaxAction.data.amount
            });
            setShowPayTaxPopup(true);
            setIsFunctionDisabled(true);
          }

          const endTurnAction = finalState.pending_actions?.find(a => a.type === 'end_turn');

          if (endTurnAction) {
            // Always show "Kết thúc lượt" button regardless of doubles
            setShowEndTurnButton(true);
          }
        }, 300);
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
      setShowBDSTab(false); // Switch back to board view

    } catch (error) {
      console.error('Error ending turn:', error);
    }
  };

  const handleBuyProperty = async (buy: boolean) => {
    if (!buyPropertyData) return;

    try {
      const response = await buyProperty({
        game_state: gameState,
        property_id: buyPropertyData.property_id,
        buy: buy
      });

      // Update game state
      onGameStateUpdate(response.new_game_state);

      // Close popup
      setShowBuyPropertyPopup(false);
      setBuyPropertyData(null);
      setIsFunctionDisabled(false);

    } catch (error) {
      console.error('Error buying property:', error);
    }
  };

  const handlePayRent = async () => {
    if (!payRentData) return;

    const currentPlayerBudget = gameState.players[gameState.current_player].budget;
    const rentAmount = payRentData.rent;

    // Check if player has enough money
    if (currentPlayerBudget < rentAmount) {
      // Enter debt mode - let player mortgage/sell properties
      setIsInDebtMode(true);
      setShowPayRentPopup(false);
      setShowBDSTab(true);
      return;
    }

    try {
      const response = await payRent({
        game_state: gameState,
        property_id: payRentData.property_id
      });

      // Update game state
      onGameStateUpdate(response.new_game_state);

      // Close popup and exit debt mode
      setShowPayRentPopup(false);
      setPayRentData(null);
      setIsInDebtMode(false);
      setIsFunctionDisabled(false);

    } catch (error) {
      console.error('Error paying rent:', error);
    }
  };

  const handleReturnToPayRent = () => {
    // Return to payment popup - player can try to pay again
    setShowBDSTab(false);
    setShowPayRentPopup(true);
  };

  const handlePayTax = async () => {
    if (!payTaxData) return;

    const currentPlayerBudget = gameState.players[gameState.current_player].budget;
    const taxAmount = payTaxData.amount;

    // Check if player has enough money
    if (currentPlayerBudget < taxAmount) {
      // Enter debt mode - let player mortgage/sell properties
      setIsInDebtMode(true);
      setShowPayTaxPopup(false);
      setShowBDSTab(true);
      return;
    }

    try {
      const response = await payTax({
        game_state: gameState
      });

      // Update game state
      onGameStateUpdate(response.new_game_state);

      // Close popup
      setShowPayTaxPopup(false);
      setPayTaxData(null);
      setIsFunctionDisabled(false);

    } catch (error) {
      console.error('Error paying tax:', error);
    }
  };

  const handlePayJailFine = async (confirm: boolean) => {
    setShowPayJailPopup(false);

    if (!confirm) {
      setForcedJailDice(null);
      return;
    }

    try {
      const response = await payJailFine({
        game_state: gameState,
        dice1: forcedJailDice?.dice1,
        dice2: forcedJailDice?.dice2
      });
      
      // If should_move is true, continue with movement
      if (response.should_move && response.dice1 !== undefined && response.dice2 !== undefined) {
        setForcedJailDice(null);
        // Call move_with_dice to continue movement with the updated state
        const moveResponse = await moveWithDice({
          game_state: response.new_game_state,
          dice1: response.dice1,
          dice2: response.dice2
        });
        
        setIsMoving(true);
        setIsFunctionDisabled(true);
        startMovementAnimation(moveResponse.intermediate_states);
      } else {
        // Update game state only if not moving
        onGameStateUpdate(response.new_game_state);
        setForcedJailDice(null);
        setIsFunctionDisabled(false);
      }

    } catch (error) {
      console.error('Error paying jail fine:', error);
      setForcedJailDice(null);
    }
  };

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
      <LeftPanel
        gameData={gameData}
        gameState={gameState}
        movementLines={movementLines}
        showEndTurnButton={showEndTurnButton}
        isFunctionDisabled={isFunctionDisabled}
        isRollDiceButtonActive={isRollDiceButtonActive}
        isAnalyzing={isAnalyzing}
        showBDSTab={showBDSTab}
        isInDebtMode={isInDebtMode}
        onEndTurn={handleEndTurn}
        onRollDice={() => {
          setBoardMessage('');
          setMovementLines([]);
          setShowBDSTab(false);
          handleCaptureFromAmberBox();
        }}
        onToggleBDSTab={() => setShowBDSTab(!showBDSTab)}
        onShowFunctionality={() => setShowFunctionalityScreen(true)}
        onClearBoard={() => {
          setBoardMessage('');
          setMovementLines([]);
        }}
        onReturnToPayRent={handleReturnToPayRent}
        onPayJailFine={() => setShowPayJailPopup(true)}
      />
      <div className='relative'>
        {showBDSTab ? (
          <BDSTab
            gameData={gameData}
            gameState={gameState}
            selectedPropertyId={selectedPropertyId}
            onPropertySelect={(propertyId) => setSelectedPropertyId(propertyId)}
            onGameStateUpdate={onGameStateUpdate}
          />
        ) : (
          <>
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
          </>
        )}
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

      {/* Buy Property Popup */}
      {showBuyPropertyPopup && buyPropertyData && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="w-[50%] h-[90%] flex flex-col justify-between gap-2 bg-gray-800 border-4 border-blue-500 rounded-lg p-4 max-w-md mx-4">
            <div className='flex flex-col'>
              <div className="text-[4vh] font-bold text-white text-center">Bạn có muốn mua BĐS {buyPropertyData.property_id}</div>
              <div className="text-[4vh] font-bold text-white text-center">với giá {formatBudget(buyPropertyData.price)}?</div>
            </div>
            <div className="h-[50%]">
              <TitleDeed
                gameData={gameData}
                gameState={gameState}
                propertyId={buyPropertyData.property_id}
              />
            </div>
            <div className="flex gap-4 justify-center">
              {
                buyPropertyData.buyable && (

                  <button
                    onClick={() => handleBuyProperty(true)}
                    className="px-5 py-3 bg-green-600 text-white rounded-lg font-bold text-[5vh] hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed"
                  >
                    Mua
                  </button>
                )
              }
              <button
                onClick={() => handleBuyProperty(false)}
                className="px-5 py-3 bg-red-600 text-white rounded-lg font-bold text-[5vh] hover:bg-red-700"
              >
                Hủy
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Pay Rent Popup */}
      {showPayRentPopup && payRentData && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="w-[50%] h-[90%] flex flex-col justify-between gap-1 bg-gray-800 border-4 border-red-500 rounded-lg p-4">
            <div className='flex flex-col'>
              <div className="text-[4vh] font-bold text-white text-center"
                style={
                  { color: gameData.color_pallete.players[payRentData.owner] }
                }
              >Trả tiền thuê BĐS {payRentData.property_id}</div>
              <div className="text-[5vh] font-bold text-red-400 text-center">{formatBudget(payRentData.rent)}</div>
              {gameState.players[gameState.current_player].budget < payRentData.rent && (
                <div className="text-[3vh] font-bold text-yellow-400 text-center">
                  Không đủ tiền! Cần thêm {formatBudget(payRentData.rent - gameState.players[gameState.current_player].budget)}
                </div>
              )}
            </div>
            <div className="h-[60%]">
              <TitleDeed
                gameData={gameData}
                gameState={gameState}
                propertyId={payRentData.property_id}
              />
            </div>
            <div className="flex gap-1 justify-center">
              <button
                onClick={handlePayRent}
                className="px-5 py-2 bg-blue-600 text-white rounded-lg font-bold text-[5vh] hover:bg-blue-700"
              >
                Tiếp tục
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Pay Jail Fine Popup */}
      {showPayJailPopup && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="w-[50%] h-auto flex flex-col gap-4 bg-gray-800 border-4 border-yellow-500 rounded-lg p-6 max-w-md mx-4">
            <div className="text-[4vh] font-bold text-white text-center">
              {gameState.players[gameState.current_player].jail_turns >= 3 ? "Bắt buộc trả 50k để ra tù!" : "Trả 50k để ra tù?"}
            </div>
            <div className="text-[3vh] text-gray-300 text-center">
              Bạn đang ở tù (Lượt {gameState.players[gameState.current_player].jail_turns}/3)
            </div>
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => handlePayJailFine(true)}
                className="px-5 py-3 bg-green-600 text-white rounded-lg font-bold text-[5vh] hover:bg-green-700"
              >
                Trả
              </button>
              {gameState.players[gameState.current_player].jail_turns < 3 && (
                <button
                  onClick={() => handlePayJailFine(false)}
                  className="px-5 py-3 bg-red-600 text-white rounded-lg font-bold text-[5vh] hover:bg-red-700"
                >
                  Hủy
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Pay Tax Popup */}
      {showPayTaxPopup && payTaxData && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          <div className="w-[50%] h-auto flex flex-col gap-4 bg-gray-800 border-4 border-yellow-500 rounded-lg p-6 max-w-md mx-4">
            <div className="text-[4vh] font-bold text-white text-center">
              {payTaxData.tax_type === 'income' ? 'Thuế Thu Nhập' : 'Thuế Xa Xỉ'}
            </div>
            <div className="text-[3vh] text-gray-300 text-center">
              Số tiền phải trả: {payTaxData.amount}k
            </div>
            {gameState.players[gameState.current_player].budget < payTaxData.amount && (
              <div className="text-[2.5vh] text-red-400 text-center">
                ⚠️ Không đủ tiền! Hãy thế chấp/bán BĐS
              </div>
            )}
            <div className="flex gap-4 justify-center">
              <button
                onClick={handlePayTax}
                className="px-5 py-3 bg-green-600 text-white rounded-lg font-bold text-[5vh] hover:bg-green-700"
              >
                Trả
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
