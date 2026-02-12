'use client'

import { formatBudget } from "@/app/utils/format";
import { GameBoardProps } from "./props";
import { CSSProperties, useState } from "react";
import { AuctionRequest } from "@/app/screen/game-screen/props";
import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { AuctionBdsCurrentChore } from "@/app/model/chore";

interface AuctionModalProps extends GameBoardProps {
  func: (_: AuctionRequest) => void;
  chore: AuctionBdsCurrentChore;
}

export function AuctionModal(props: AuctionModalProps) {
  const { gameState, func, chore } = props;
  const { player, original_price, current_price } = chore;
  const budget = gameState.logic.player[player].budget;

  const buttonClassName = "px-[1cqw] py-[1cqh] text-[2.5cqh] rounded bg-(--bg-color) border-2 border-white disabled:text-white whitespace-nowrap";
  const bds_info = chore.bds;
  let text = `Đấu giá BĐS ${bds_info}, giá gốc ${formatBudget(original_price)}`;

  const prices = [1, 10, 0, 50, 100];

  const [price, setPrice] = useState<number | null>(null);

  return (
    <div className="w-full h-full flex flex-col gap-[1vw]">
      <div className="w-full flex min-h-[10%]">
        {
          chore.players.map((p) =>
            <div
              key={p}
              style={{ "--bg-color": COLOR_UI_INFO[p].lightColorCode, "--bd-color": p == player ? "black" : "white" } as CSSProperties}
              className="w-[15%] h-full bg-(--bg-color) border-2 border-(--bd-color)">
            </div>)
        }
      </div>
      <div className="w-full flex flex-col">
        <div className="w-full flex justify-center whitespace-nowrap text-[3cqh]">{text}</div>
        <div className="w-full flex flex-row justify-evenly items-center text-[3cqh] font-bold">
          <div className="flex-1 flex justify-center whitespace-nowrap">{formatBudget(current_price)}</div>
          <div className="flex-1 flex justify-center whitespace-nowrap">→</div>
          <div className="flex-1 flex justify-center whitespace-nowrap">{(price != null && price != 0) ? formatBudget(current_price + price) : ""}</div>
        </div>
      </div>
      <div className="w-full grid grid-cols-3 grid-rows-2 justify-center gap-[0.25vw] px-[1vw]">
        {
          prices.map((p) =>
            <button
              key={p}
              style={{ "--bg-color": p != price ? COLOR_UI_INFO[player].lightColorCode : "white" } as CSSProperties}
              className={buttonClassName + (p == price ? " font-bold" : "")}
              disabled={p > 0 ? current_price + p >= budget : undefined}
              onClick={p != price ? () => setPrice(p) : () => setPrice(null)}
            >{p > 0 ? formatBudget(p) : "Rút lui"}
            </button>
          )
        }
        <button
          style={{ "--bg-color": "red" } as React.CSSProperties}
          className={buttonClassName + " font-bold"}
          disabled={price == null}
          onClick={price != null ? () => { func({ amount: price }); setPrice(null); } : undefined}
        >Chốt hạ
        </button>
      </div>
    </div>
  );
}
