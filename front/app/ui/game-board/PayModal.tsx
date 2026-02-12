'use client'

import { formatBudget } from "@/app/utils/format";
import { GameBoardProps } from "./props";
import { NumRequest } from "@/app/screen/game-screen/props";
import { CSSProperties } from "react";
import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { PayChore } from "@/app/model/chore";

interface PayModalProps extends GameBoardProps {
  func: (_: NumRequest) => void;
  chore: PayChore;
}

export function PayModal(props: PayModalProps) {
  const { gameState, func, chore } = props;
  const { amount, player, receiver } = chore;
  const player_budget = gameState.logic.player[player].budget;
  const buttonClassName = "px-[7cqw] py-[3cqw] rounded disabled:text-white disabled:bg-gray-300 border-2 border-white";
  let text = `Trả ${formatBudget(amount)}`;

  if (chore.bds != null) {
    const bds = chore.bds;
    text = `BĐS ${bds} đã có chủ, trả ${formatBudget(amount)}.`;
  }

  return (
    <div className="w-full h-full flex flex-col gap-[1.5vw] justify-center">
      <div className="w-full flex h-[10%]">
        <div
          style={{ "--bg-color": COLOR_UI_INFO[player].lightColorCode, "--bd-color": "black" } as CSSProperties}
          className="w-[15%] h-full bg-(--bg-color) border-2 border-(--bd-color)">
        </div>
        {
          receiver != null &&
          <div
            style={{ "--bg-color": COLOR_UI_INFO[receiver].lightColorCode, "--bd-color": "black" } as CSSProperties}
            className="w-[15%] h-full bg-(--bg-color) border-2 border-(--bd-color)">
          </div>
        }
      </div>
      <div className="w-full flex justify-center font-bold whitespace-nowrap text-[6cqw]">{text}</div>
      <div className="w-full flex justify-center gap-[1.5vw] text-[6cqw]">
        <button className={buttonClassName + " bg-yellow-300"} disabled={player_budget < amount} onClick={() => func({ response: 1 })}>Trả</button>
      </div>
    </div>
  );
}

