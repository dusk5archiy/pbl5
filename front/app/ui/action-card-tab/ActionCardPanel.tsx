import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { CSSProperties } from "react";
import { GameBoardProps } from "../game-board/props";

export function ActionCardPanel(props: GameBoardProps) {
  const { gameState, selectedActionGroup, selectedActionCard, useActionCardFunc, tradeFunc, setPropertyTab, guest } = props;
  const owner = gameState.logic.action[selectedActionGroup][selectedActionCard].owner;
  const text_color = owner == null ? "text-gray-100" : "text-black";
  const viewing_player = gameState.logic.viewing_player;
  const can_interact = guest == null || guest == viewing_player;
  const can_use = can_interact && gameState.ui.action[selectedActionGroup][selectedActionCard].can_use;
  const can_choose = can_interact && gameState.ui.action[selectedActionGroup][selectedActionCard].can_choose;
  const trade_chore = gameState.current_chore.trade;

  return (
    <div className="@container w-full h-full flex gap-[0.5vw] justify-between">
      <div
        style={
          {
            "--bg-color": owner == null ? undefined : COLOR_UI_INFO[owner].lightColorCode
          } as CSSProperties
        }
        className={
          `flex-1 h-full flex flex-col justify-center px-[0.5vw] border-2 border-white rounded ${owner == null ? "" : `bg-(--bg-color)`}`
        }>
        <div className={`w-full flex justify-center ${text_color} text-[3cqw]`}>Tình trạng</div>
        <div className={`w-full flex justify-center ${text_color} font-bold text-[4cqw]`}>
          {owner != null ? "Đã sở hữu" : "Chưa sở hữu"}
        </div>
      </div>
      <button
        style={{ "--bg-color": (owner == null || owner != viewing_player || !can_use) ? "#D1D5DB" : COLOR_UI_INFO[owner].lightColorCode } as CSSProperties}
        className="flex-1 flex flex-col justify-center overflow-hidden font-bold rounded border-2 border-white disabled:text-white whitespace-nowrap bg-(--bg-color) active:bg-gray-400 disabled:active:bg-(--bg-color)"
        disabled={!can_use}
        onClick={() => useActionCardFunc({ group: selectedActionGroup, card: selectedActionCard })}
      >
        <div className="text-[5cqw]">Sử dụng</div>
      </button>
      <button
        style={{ "--bg-color": "#D1D5DB" } as CSSProperties}
        className="flex-1 flex flex-col justify-center overflow-hidden font-bold rounded border-2 border-white disabled:text-white whitespace-nowrap bg-(--bg-color) active:bg-gray-400 disabled:active:bg-(--bg-color)"
        disabled={!can_choose}
        onClick={
          trade_chore != null ? () => {
            setPropertyTab("trade");
            tradeFunc({ card: { group: selectedActionGroup, card: selectedActionCard } });
          } : undefined
        }
      >
        <div className="text-[5cqw]">Chọn</div>
      </button>
    </div>
  );

}

