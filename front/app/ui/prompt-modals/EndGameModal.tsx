import { formatBudget } from "@/app/utils/format";
import { GameBoardProps } from "../game-board/props";
import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { CSSProperties } from "react";
import { EndGameChore } from "@/app/model/chore";

interface EndGameModalProps extends GameBoardProps {
  chore: EndGameChore;
}

export function EndGameModal(
  props: EndGameModalProps
) {
  const { gameState, chore } = props;
  const { player_order } = chore;
  const buttonClassName = "p-[0.5vw] rounded disabled:text-white disabled:bg-gray-300 border-2 border-white";
  
  console.log(gameState);

  return (
    <div className="w-full h-full flex flex-col gap-[1.5vw] justify-center">
      <div className="w-full flex justify-center font-bold whitespace-nowrap text-[4cqw]">Trò chơi kết thúc</div>
      <div className="w-full grid grid-cols-3 grid-rows-2 text-[4cqw] gap-[0.5vw] p-[0.5vw]">
        {
          player_order.map(
            (playerId) =>
              <div
                key={playerId}
                style={{ "--bg-color": COLOR_UI_INFO[playerId].lightColorCode } as CSSProperties}
                className={buttonClassName + ` bg-(--bg-color)`}>
                {formatBudget(gameState.ui.player[playerId].total)}
              </div>
          )
        }
      </div>
    </div>
  );
}
