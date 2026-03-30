'use client'

import { formatBudget } from "@/app/utils/format";
import { GameBoardProps } from "../game-board/props";
import { NumRequest } from "@/app/screen/game-screen/props";
import { BuyChore } from "@/app/model/chore";

interface BuyModalProps extends GameBoardProps {
  func: (_: NumRequest) => void;
  chore: BuyChore;
}

export function BuyModal(props: BuyModalProps) {
  const { gameState, func: buyFunc, chore, guest } = props;
  if (guest != null && guest != gameState.logic.viewing_player) {
    return undefined;
  }
  const { bds, price, player } = chore;
  const can_buy = gameState.logic.budget[player] >= price;
  const buttonClassName = "px-[7cqw] py-[5cqw] rounded disabled:text-white disabled:bg-gray-300 border-2 border-white";
  return (
    <div className="w-full h-full flex flex-col gap-[1.5vw] justify-center">
      <div className="w-full flex justify-center font-bold whitespace-nowrap text-[4cqw]">Bạn có muốn mua BĐS {bds} với giá {formatBudget(price)}?</div>
      <div className="w-full flex justify-evenly px-[1.5vw] gap-[1.5vw] text-[6cqw]">
        <button className={buttonClassName + " bg-blue-300"} disabled={!can_buy} onClick={() => buyFunc({ response: 1 })}>Mua</button>
        <button className={buttonClassName + " bg-yellow-300"} onClick={() => buyFunc({ response: 0 })}>Đấu giá</button>
      </div>
    </div>
  );
}
