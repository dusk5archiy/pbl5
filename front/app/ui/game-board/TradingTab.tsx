import { formatBudget } from "@/app/utils/format";
import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { CSSProperties } from "react";
import { GameBoardProps } from "./props";
import { TradeChore, TradeItem } from "@/app/model/chore";

export function SelectPlayerTab(props: GameBoardProps) {
  const {
    gameState,
    tradeFunc,
    setBdsShown
  } = props;

  const start_trade_chore = gameState.current_chore.start_trade;
  if (start_trade_chore == null) {
    return null;
  }
  return (
    <div className="w-full h-full flex flex-col gap-[3vw]">
      <div className="h-[10%]"></div>
      <div className="w-full flex justify-center font-bold whitespace-nowrap text-[3cqw] text-white">
        Chọn người chơi để trao đổi:
      </div>
      <div className="w-full flex justify-evenly px-[1.5vw] gap-[1.5vw]">
        {
          start_trade_chore.players.map((p) =>
            <button
              key={p}
              style={{ "--bg-color": COLOR_UI_INFO[p].lightColorCode } as CSSProperties}
              className="p-[6cqw] bg-(--bg-color) rounded border-2 border-white"
              onClick={() => {
                setBdsShown(0);
                tradeFunc({ player_2: p });
              }}
            >
            </button>
          )
        }
      </div>
    </div>
  );
}

function TradePlayerComponent(
  props: GameBoardProps & {
    player: string,
    trade_item: TradeItem,
    onPriceClick: (_: number) => void,
    trade_chore: TradeChore
  }
) {
  const { player, trade_item, trade_chore, onPriceClick, focusBds, setPropertyTab, setSelectedActionCard, setSelectedActionGroup } = props;
  const selector_class_name = "flex-1 max-h-full flex flex-col w-[23%] overflow-y-auto gap-[0.5vw] p-[0.5vw] border-2 border-white rounded-lg";
  const option_class_name = "w-full flex justify-center rounded whitespace-nowrap text-[3cqw] active:bg-gray-400 py-[2vw]";
  const prices = [100, 50, 10, 1, 0];
  return (
    <div
      style={
        { "--border": COLOR_UI_INFO[player].lightColorCode } as CSSProperties
      }
      className="flex-1 h-full flex flex-col overflow-y-auto gap-[0.5vw] p-[0.5vw] border-4 border-(--border) rounded-xl"
    >
      <div className="w-full h-[50%] flex gap-[0.25vw]">
        <div className={selector_class_name}>
          {
            trade_item.bds.map(
              (bds) => (
                <button key={bds}
                  style={
                    {
                      "--bg-color": COLOR_UI_INFO[player].lightColorCode,
                    } as React.CSSProperties
                  }
                  className={option_class_name + " bg-(--bg-color) disabled:active:bg-(--bg-color)"}
                  onClick={() => { focusBds(bds); setPropertyTab("bds"); }}
                  disabled={trade_chore.confirm_mode}
                >{bds}
                </button>
              )
            )
          }
        </div>
        <div className={selector_class_name}>
          {
            trade_item.card.map(
              ({ group, card }) => (
                <button key={`${group}.${card}`}
                  style={
                    {
                      "--bg-color": COLOR_UI_INFO[player].lightColorCode,
                    } as React.CSSProperties
                  }
                  className={option_class_name + " bg-(--bg-color) disabled:active:bg-(--bg-color)"}
                  disabled={trade_chore.confirm_mode}
                  onClick={() => { setSelectedActionGroup(group); setSelectedActionCard(card); setPropertyTab("action_card"); }}
                >{`${group}.${card}`}
                </button>
              )
            )
          }
        </div>
      </div>
      <div className="w-full h-[30%] flex flex-col">
        <div className="w-full h-[50%] flex justify-center font-bold items-center text-white text-[3cqw]">{formatBudget(trade_item.money)}</div>
        <div className="w-full h-[50%] flex gap-[0.25vw]">
          {
            prices.map((price) =>
              <button
                key={price}
                style={
                  {
                    "--bg-color": COLOR_UI_INFO[player].lightColorCode,
                  } as React.CSSProperties
                }
                className="flex-1 whitespace-nowrap bg-(--bg-color) rounded-lg p-[0.25vw] text-[2.5cqw] disabled:text-white"
                onClick={() => onPriceClick(price)}
                disabled={trade_chore.confirm_mode}
              >
                {price == 0 ? formatBudget(price) : `+${formatBudget(price)}`}
              </button>
            )
          }
        </div>
      </div>
      <div className="w-full flex-1 flex flex-col justify-center items-center text-white">
        <div className="text-[2cqw]">Tổng cộng</div>
        <div className="text-[3cqw] font-bold">{formatBudget(trade_item.total)}</div>
      </div>
    </div>
  );
}


export function TradingTab(props: GameBoardProps) {
  const {
    gameState,
    tradeFunc,
  } = props;
  const trade_chore = gameState.current_chore.trade;
  if (trade_chore == null) {
    return null;
  }
  return (
    <div className="w-full h-full flex">
      <div className="w-full h-full flex gap-[0.5vw] justify-between">
        <TradePlayerComponent {...{ ...props, trade_chore: trade_chore, player: trade_chore.player_1, trade_item: trade_chore.player_1_item, onPriceClick: (price) => tradeFunc({ money_1: price }) }} />
        <TradePlayerComponent {...{ ...props, trade_chore: trade_chore, player: trade_chore.player_2, trade_item: trade_chore.player_2_item, onPriceClick: (price) => tradeFunc({ money_2: price }) }} />
      </div>
    </div>
  );
}


