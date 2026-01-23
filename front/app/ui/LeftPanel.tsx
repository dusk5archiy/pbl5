import PropertyBoard from './PropertyBoard';
import { GameData, GameState } from '@/app/game/model';
import { formatBudget } from './lib/utils';

interface LeftPanelProps {
  gameData: GameData;
  gameState: GameState;
  movementLines: { from: string, to: string, isLast: boolean }[];
  showEndTurnButton: boolean;
  isFunctionDisabled: boolean;
  isRollDiceButtonActive: boolean;
  isAnalyzing: boolean;
  showBDSTab: boolean;
  isInDebtMode?: boolean;
  onEndTurn: () => void;
  onRollDice: () => void;
  onToggleBDSTab: () => void;
  onShowFunctionality: () => void;
  onClearBoard: () => void;
  onReturnToPayRent?: () => void;
}

export default function LeftPanel({
  gameData,
  gameState,
  movementLines,
  showEndTurnButton,
  isFunctionDisabled,
  isRollDiceButtonActive,
  isAnalyzing,
  showBDSTab,
  isInDebtMode = false,
  onEndTurn,
  onRollDice,
  onToggleBDSTab,
  onShowFunctionality,
  onClearBoard,
  onReturnToPayRent
}: LeftPanelProps) {
  const current_player_color = gameData.color_pallete.players[gameState.current_player];

  return (
    <div className="flex flex-col w-[40vw] gap-1 overflow-hidden">
      {/*Game Board */}
      <div
        className="flex gap-1 border-2 border-white p-1 rounded h-[25%] bg-[#446655] items-center cursor-pointer active:opacity-50"
        onClick={onShowFunctionality}
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
                <span className="font-bold text-[5vh] text-gray-100 whitespace-nowrap">{`${gameState.houses_left} • ${gameState.hotels_left}`}</span>
              </div>
            </div>
          </div>
          <button
            onClick={onEndTurn}
            className="flex-1 text-[5vh] font-bold rounded border-2 border-gray-500 disabled:text-white active:opacity-50"
            style={{ backgroundColor: current_player_color }}
            disabled={!showEndTurnButton || isFunctionDisabled}
          >
            Kết thúc lượt
          </button>
        </div>
        <div className='flex flex-col flex-1 gap-1'>
          <div className='flex flex-col h-[70%] gap-1'>
            <button
              onClick={onRollDice}
              className="w-full h-[50%] text-[5vh] text-gray-600 font-bold rounded border-3 border-gray-500 disabled:text-white active:opacity-50"
              disabled={!isRollDiceButtonActive || isAnalyzing || isFunctionDisabled || showBDSTab}
              style={{ backgroundColor: current_player_color }}
            >
              Thảy
            </button>
            <button
              onClick={onToggleBDSTab}
              disabled={!isInDebtMode && isFunctionDisabled}
              className="w-full h-[50%] border-2 text-[5vh] border-gray-600 font-bold py-1 rounded text-gray-700 disabled:text-white bg-white active:opacity-50"
            >BĐS
            </button>
          </div>
          <button
            onClick={isInDebtMode ? onReturnToPayRent : onClearBoard}
            className="w-full flex-1 text-[5vh] text-gray-600 font-bold rounded border-3 border-gray-500 disabled:text-white active:opacity-50"
            disabled={!isInDebtMode}
            style={{ backgroundColor: current_player_color }}
          >
            Tiếp
          </button>
        </div>
      </div>
    </div>
  );
}
