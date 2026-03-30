import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { GameBoardProps } from "../game-board/props";
import { SelectPlayerTab, TradingTab } from "./TradingTab";

function NormalTradeTab(props: GameBoardProps) {
  const {
    gameState,
    startTradeFunc,
    guest
  } = props;

  const BUTTON_CLASS = "w-max h-max px-[4cqw] py-[2cqw] text-[3cqw] font-bold bg-(--bg-color) rounded active:bg-[lightgray] disabled:text-white disabled:active:bg-(--bg-color)";
  const player = gameState.logic.viewing_player;
  const can_interact = guest == null || guest == player;
  const ui_player = guest || player;
  const color = COLOR_UI_INFO[ui_player].lightColorCode;

  return (
    <div className="w-full h-full flex justify-center items-center gap-[1vw]">
      <button
        style={
          {
            '--bg-color': color
          } as React.CSSProperties
        }
        disabled={!can_interact || !gameState.effect.can_trade}
        className={BUTTON_CLASS}
        onClick={() => {
          startTradeFunc();
        }}
      >Trao đổi
      </button>
    </div>
  );

}

export function TradeTab(props: GameBoardProps) {
  const { gameState } = props;
  const start_trade_chore = gameState.current_chore.start_trade;
  const trade_chore = gameState.current_chore.trade;
  return (
    <div className="@container w-full h-full flex flex-col gap-[5vw]">
      <div className="w-full h-full flex">
        {
          start_trade_chore != null ?
            <SelectPlayerTab {...props} /> :
            trade_chore != null ?
              <TradingTab {...props} /> :
              <NormalTradeTab {...props} />
        }
      </div>
    </div>
  );
}


