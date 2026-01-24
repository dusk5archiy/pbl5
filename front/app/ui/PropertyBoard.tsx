import { GameData, GameState } from '@/app/game/model';

interface PropertyBoardProps {
  gameData: GameData;
  gameState: GameState;
  showBorders: boolean;
}

export default function PropertyBoard({ gameData, gameState, showBorders }: PropertyBoardProps) {
  return (
    <div className='flex w-full gap-[1vw] justify-evenly'>
      <div className="flex gap-[0.5vw] active:opacity-50">
        {/* Columns */}
        {gameData.bds_groups_order.map((group) => (
          <div key={group} className="flex flex-col-reverse gap-[1vh] justify-start">
            {/* Cells for this column */}
            {gameData.group_bds[group]?.map((spaceId) => {
              const bdsState = gameState.bds[spaceId];
              const isOwned = bdsState && bdsState.owner !== "";
              const bgColor = isOwned ? gameData.color_pallete.players[bdsState.owner] : 'gray';
              const textColor = isOwned ? 'black' : 'white';
              const displayText = isOwned ? (bdsState.level === -1 ? '/' : bdsState.level.toString()) : group;

              // Check if the current player is at this space (only when movement lines are present)
              const playerAtSpace = showBorders && gameState.players[gameState.current_player]?.at === spaceId;
              const borderColor = playerAtSpace ? gameData.color_pallete.players[gameState.current_player] : '#1f2937';
              const borderWidth = playerAtSpace ? 'border-3' : 'border-2';

              return (
                <div
                  key={spaceId}
                  style={{
                    backgroundColor: bgColor,
                    color: textColor,
                    borderColor: borderColor,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: '400',
                    textAlign: 'center'
                  }}
                  className={`h-[4vh] ${borderWidth} aspect-square overflow-hidden`}
                >
                  <span className='text-[3.9vh]'>{displayText}</span>
                </div>
              );
            })}
          </div>
        ))}
      </div>
      <div className="flex flex-col gap-1 justify-end">
        {/* Display keep cards from game data */}
        {Object.entries(gameData.kv)
          .filter(([_, card]) => card.keep)
          .map(([cardId, _]) => {
            const cardOwner = gameState.cards[cardId];
            const isOwned = cardOwner && cardOwner !== "";
            const bgColor = isOwned ? gameData.color_pallete.players[cardOwner] : 'gray';
            const textColor = isOwned ? 'black' : 'white';

            return (
              <div
                key={cardId}
                style={{
                  backgroundColor: bgColor,
                  color: textColor,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: '400',
                  textAlign: 'center'
                }}
                className="w-[7vw] h-[4vh] border-2 overflow-hidden border-gray-800"
              >
                <span className='text-[3.9vh]'>{cardId}</span>
              </div>
            );
          })
        }
        {Object.entries(gameData.ch)
          .filter(([_, card]) => card.keep)
          .map(([cardId, _]) => {
            const cardOwner = gameState.cards[cardId];
            const isOwned = cardOwner && cardOwner !== "";
            const bgColor = isOwned ? gameData.color_pallete.players[cardOwner] : 'gray';
            const textColor = isOwned ? 'black' : 'white';

            return (
              <div
                key={cardId}
                style={{
                  backgroundColor: bgColor,
                  color: textColor,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: '400',
                  textAlign: 'center'
                }}
                className="w-[7vw] h-[4vh] border-2 overflow-hidden border-gray-800"
              >
                <span className='text-[3.9vh]'>{cardId}</span>
              </div>
            );
          })
        }
      </div>
    </div>
  );
}
