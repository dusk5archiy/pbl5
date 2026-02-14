'use client'

import { formatBudget } from "@/app/utils/format";
import { GameBoardProps } from "./props";
import { NumRequest } from "@/app/screen/game-screen/props";
import { CSSProperties } from "react";
import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { ReceiveMortgageChore } from "@/app/model/chore";

interface ReceiveMortgageModalProps extends GameBoardProps {
  func: (_: NumRequest) => void;
  chore: ReceiveMortgageChore;
}

export function ReceiveMortgageModal(props: ReceiveMortgageModalProps) {
  const { gameState, func, chore } = props;
  const { unmortgage, interest, bds, player } = chore;
  const player_budget = gameState.logic.budget[player];
  const buttonClassName = "p-[1vw] rounded disabled:text-white disabled:bg-gray-300 border-2 border-white";
  const text = `Bạn muốn chuộc BĐS ${bds} không?`;


  return (
    <div className="@container w-full h-full flex flex-col gap-[1.5vw] justify-center">
      <div className="w-full flex h-[10%]">
        <div
          style={{ "--bg-color": COLOR_UI_INFO[player].lightColorCode, "--bd-color": "black" } as CSSProperties}
          className="w-[15%] h-full bg-(--bg-color) border-2 border-(--bd-color)">
        </div>
      </div>
      <div className="w-full flex justify-center font-bold whitespace-nowrap text-[5cqw]">{text}</div>
      <div className="w-full flex justify-center gap-[1.5vw] text-[6cqw]">
        <button
          className={buttonClassName + " bg-yellow-300"}
          disabled={player_budget < unmortgage}
          onClick={() => func({ response: 1 })}
        >
          Có (-{formatBudget(unmortgage)})
        </button>
        <button
          className={buttonClassName + " bg-orange-300"}
          disabled={player_budget < interest}
          onClick={() => func({ response: 2 })}
        >
          Không (-{formatBudget(interest)})
        </button>
      </div>
    </div>
  );
}


