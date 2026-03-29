'use client'

import { GameBoardProps } from "./props";
import { NumRequest } from "@/app/screen/game-screen/props";
import { CSSProperties } from "react";
import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { TradeChore } from "@/app/model/chore";

interface PayModalProps extends GameBoardProps {
  func: (_: NumRequest) => void;
  chore: TradeChore;
}

export function TradeModal(props: PayModalProps) {
  const { func, chore, guest, gameState } = props;
  const { player, player_1, player_2 } = chore;
  if (guest != null && guest != gameState.logic.viewing_player) {
    return undefined;
  }
  const buttonClassName = "p-[1vw] rounded disabled:text-white disabled:bg-gray-300 border-2 border-white";

  if (!chore.confirm_mode) {
    return (
      <div className="w-full h-full flex flex-col gap-[1.5vw] justify-center">
        <div className="w-full flex h-[10%] mb-[4%]">
          <div
            style={{ "--bg-color": COLOR_UI_INFO[player].lightColorCode, "--bd-color": "black" } as CSSProperties}
            className="w-[15%] h-full bg-(--bg-color) border-2 border-(--bd-color)">
          </div>
          <div
            style={{ "--bg-color": COLOR_UI_INFO[player_1].lightColorCode, "--bd-color": "black" } as CSSProperties}
            className="w-[15%] h-full bg-(--bg-color) border-2 border-(--bd-color)">
          </div>
          <div
            style={{ "--bg-color": COLOR_UI_INFO[player_2].lightColorCode, "--bd-color": "black" } as CSSProperties}
            className="w-[15%] h-full bg-(--bg-color) border-2 border-(--bd-color)">
          </div>
        </div>
        <div className="w-full flex justify-center font-bold text-[5cqw] text-center">Chọn BĐS và Thẻ<br /> trong các tab BĐS và Thẻ</div>
        <div className="w-full flex justify-center gap-[1vw] text-[6cqw]">
          <button className={buttonClassName + " bg-green-300"} onClick={() => func({ response: 1 })}>Yêu cầu trao đổi</button>
          <button className={buttonClassName + " bg-red-300"} onClick={() => func({ response: 0 })}>Hủy trao đổi</button>
        </div>
      </div>
    );
  } else {
    return (
      <div className="w-full h-full flex flex-col gap-[1vw] justify-center">
        <div className="w-full flex h-[10%]">
          <div
            style={{ "--bg-color": COLOR_UI_INFO[player].lightColorCode, "--bd-color": "black" } as CSSProperties}
            className="w-[15%] h-full bg-(--bg-color) border-2 border-(--bd-color)">
          </div>
        </div>
        <div className="w-full flex justify-center font-bold text-[5cqw] text-center">Chấp nhận trao đổi?</div>
        <div className="w-full flex flex-col justify-center items-center gap-[0.5vw] text-[6cqw]">
          <div className="flex gap-[1vw]">
            <button className={buttonClassName + " bg-green-300"} onClick={() => func({ response: 1 })}>Chấp nhận</button>
            <button className={buttonClassName + " bg-red-300"} onClick={() => func({ response: 0 })}>Từ chối</button>
          </div>
          <div className="flex gap-[1vw]">
            <button className={buttonClassName + " bg-yellow-300"} onClick={() => func({ response: 2 })}>Sửa yêu cầu</button>
          </div>
        </div>
      </div>
    );
  }
}


