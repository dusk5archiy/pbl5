import { GameBoardProps } from "@/app/ui/game-board/props";
import { CSSProperties, useState } from "react";
import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { formatBudget } from "@/app/utils/format";

export function BudgetPanel(props: GameBoardProps) {
  const { gameState } = props;
  const [budgetMode, setBudgetMode] = useState<boolean>(true);
  return (
    <div
      className="@container w-full h-full flex flex-col gap-[1vh] border-2 border-white p-[0.25vw] rounded bg-gray-700 justify-center"
      onClick={() => setBudgetMode(!budgetMode)}
    >
      {Object.entries(gameState.logic.player).map(([playerId, playerData]: [string, any]) => (
        <div
          key={playerId}
          className="w-full h-[14%] flex items-center pl-[0.25vw] gap-[1vw] overflow-hidden"
        >
          <div
            className="flex items-center justify-center h-full w-[10%] min-w-2"
            style={{
              backgroundColor: COLOR_UI_INFO[playerId].lightColorCode
            }}
          />
          {
            budgetMode ?
              <div
                style={{
                  "--text-color": gameState.logic.player[playerId].alive ? "#F3F4F6" : "#99a1af",
                } as CSSProperties}
                className="flex-1 h-full flex items-center font-bold text-(--text-color) text-[15cqw] overflow-hidden"
              >{formatBudget(playerData.budget)}
              </div> :
              gameState.logic.player[playerId].alive ?
                <div
                  style={{
                    "--text-color": "#d1d5db",
                  } as CSSProperties}
                  className="flex-1 h-full flex items-center font-bold text-(--text-color) text-[15cqw] overflow-hidden"
                >
                  {`• ${formatBudget(gameState.ui.player[playerId].total)}`}
                </div>
                : undefined
          }
        </div>
      ))}
    </div>
  );
}


