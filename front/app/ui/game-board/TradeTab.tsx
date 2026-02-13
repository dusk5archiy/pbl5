import { formatBudget } from "@/app/utils/format";
import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { CSSProperties, useState } from "react";
import { GameBoardProps } from "./props";

function NormalTradeTab(props: GameBoardProps & { setRuleEnabled: (_: boolean) => void }) {
  const {
    gameState,
    startTradeFunc,
    payFunc, receiveMortgageFunc, jailFunc,
    setRuleEnabled
  } = props;
  const pay_chore = gameState.current_chore.pay;
  const receive_mortgage_chore = gameState.current_chore.receive_mortgage;
  const jail_chore = gameState.current_chore.jail;

  const BUTTON_CLASS = "w-max h-max px-[4cqw] py-[2cqw] text-[3cqw] font-bold bg-(--bg-color) rounded active:bg-[lightgray] disabled:text-white disabled:active:bg-(--bg-color)";
  const player = gameState.logic.viewing_player || gameState.logic.current_player;

  return (
    <div className="w-full h-full flex justify-center items-center gap-[1vw]">
      <button
        style={
          {
            '--bg-color': COLOR_UI_INFO[player].lightColorCode
          } as React.CSSProperties
        }
        disabled={!gameState.effect.can_trade}
        className={BUTTON_CLASS}
        onClick={startTradeFunc}
      >Trao đổi
      </button>
      <button
        style={
          {
            '--bg-color': COLOR_UI_INFO[player].lightColorCode
          } as React.CSSProperties
        }
        onClick={
          pay_chore != null ?
            () => payFunc({ response: 0 }) :
            receive_mortgage_chore != null ?
              () => receiveMortgageFunc({ response: 0 }) :
              jail_chore != null ?
                () => jailFunc({ response: 0 }) :
                undefined
        }
        disabled={
          pay_chore == null
          && receive_mortgage_chore == null
          && jail_chore == null
        }
        className={BUTTON_CLASS}
      >Phá sản
      </button>
      <button
        style={
          {
            '--bg-color': COLOR_UI_INFO[player].lightColorCode
          } as React.CSSProperties
        }
        onClick={() => setRuleEnabled(true)}
        className={BUTTON_CLASS}
      >Luật chơi
      </button>
    </div>
  );

}

function SelectPlayerTab(props: GameBoardProps) {
  const {
    gameState,
    tradeFunc,
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
              onClick={() => tradeFunc({ player_2: p })}
            >
            </button>
          )
        }
      </div>
    </div>
  );
}

function TradingTab(props: GameBoardProps) {
  const {
    gameState,
    tradeFunc,
    focusBds,
    setPropertyTab,
    setSelectedActionGroup,
    setSelectedActionCard,
  } = props;
  const trade_chore = gameState.current_chore.trade;
  const selector_class_name = "flex-1 max-h-full flex flex-col w-[23%] overflow-y-auto gap-[0.5vw] p-[0.5vw] border-2 border-white rounded-lg";
  const option_class_name = "w-full flex justify-center rounded whitespace-nowrap text-[3cqw] active:bg-gray-400 py-[2vw]";
  const prices = [100, 50, 10, 1, 0];
  if (trade_chore == null) {
    return null;
  }
  return (
    <div className="w-full h-full flex">
      <div className="w-full h-full flex gap-[0.5vw] justify-between">
        <div
          style={
            { "--border": COLOR_UI_INFO[trade_chore.player_1].lightColorCode } as CSSProperties
          }
          className="flex-1 h-full flex flex-col overflow-y-auto gap-[0.5vw] p-[0.5vw] border-4 border-(--border) rounded-xl"
        >
          <div className="w-full h-[50%] flex gap-[0.25vw]">
            <div className={selector_class_name}>
              {
                trade_chore.player_1_item.bds.map(
                  (bds) => (
                    <button key={bds}
                      style={
                        {
                          "--bg-color": COLOR_UI_INFO[trade_chore.player_1].lightColorCode,
                        } as React.CSSProperties
                      }
                      className={option_class_name + " bg-(--bg-color) disabled:active:bg-(--bg-color)"}
                      onClick={() => { focusBds(bds); setPropertyTab(0); }}
                      disabled={trade_chore.confirm_mode}
                    >{bds}
                    </button>
                  )
                )
              }
            </div>
            <div className={selector_class_name}>
              {
                trade_chore.player_1_item.card.map(
                  ({ group, card }) => (
                    <button key={`${group}.${card}`}
                      style={
                        {
                          "--bg-color": COLOR_UI_INFO[trade_chore.player_1].lightColorCode,
                        } as React.CSSProperties
                      }
                      className={option_class_name + " bg-(--bg-color) disabled:active:bg-(--bg-color)"}
                      disabled={trade_chore.confirm_mode}
                      onClick={() => { setSelectedActionGroup(group); setSelectedActionCard(card); setPropertyTab(1); }}
                    >{`${group}.${card}`}
                    </button>
                  )
                )
              }
            </div>
          </div>
          <div className="w-full h-[30%] flex flex-col">
            <div className="w-full h-[50%] flex justify-center font-bold items-center text-white text-[3cqw]">{formatBudget(trade_chore.player_1_item.money)}</div>
            <div className="w-full h-[50%] flex gap-[0.25vw]">
              {
                prices.map((price) =>
                  <button
                    key={price}
                    style={
                      {
                        "--bg-color": COLOR_UI_INFO[trade_chore.player_1].lightColorCode,
                      } as React.CSSProperties
                    }
                    className="flex-1 whitespace-nowrap bg-(--bg-color) rounded-lg p-[0.25vw] text-[2.5cqw] disabled:text-white"
                    onClick={() => tradeFunc({ money_1: price })}
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
            <div className="text-[3cqw] font-bold">{formatBudget(trade_chore.player_1_item.total)}</div>
          </div>
        </div>
        <div
          style={
            { "--border": COLOR_UI_INFO[trade_chore.player_2].lightColorCode } as CSSProperties
          }
          className="flex-1 h-full flex flex-col overflow-y-auto gap-[0.5vw] p-[0.5vw] border-4 border-(--border) rounded-xl"
        >
          <div className="w-full h-[50%] flex gap-[0.25vw]">
            <div className={selector_class_name}>
              {
                trade_chore.player_2_item.bds.map(
                  (bds) => (
                    <button key={bds}
                      style={
                        {
                          "--bg-color": COLOR_UI_INFO[trade_chore.player_2].lightColorCode,
                        } as React.CSSProperties
                      }
                      className={option_class_name + " bg-(--bg-color) disabled:active:bg-(--bg-color)"}
                      disabled={trade_chore.confirm_mode}
                      onClick={() => { focusBds(bds); setPropertyTab(0); }}
                    >{bds}
                    </button>
                  )
                )
              }
            </div>
            <div className={selector_class_name}>
              {
                trade_chore.player_2_item.card.map(
                  ({ group, card }) => (
                    <button key={`${group}.${card}`}
                      style={
                        {
                          "--bg-color": COLOR_UI_INFO[trade_chore.player_2].lightColorCode,
                        } as React.CSSProperties
                      }
                      className={option_class_name + " bg-(--bg-color) disabled:active:bg-(--bg-color)"}
                      onClick={() => { setSelectedActionGroup(group); setSelectedActionCard(card); setPropertyTab(1); }}
                      disabled={trade_chore.confirm_mode}
                    >{`${group}.${card}`}
                    </button>
                  )
                )
              }
            </div>
          </div>
          <div className="w-full h-[30%] flex flex-col">
            <div className="w-full h-[50%] flex justify-center font-bold items-center text-white text-[3cqw]">{formatBudget(trade_chore.player_2_item.money)}</div>
            <div className="w-full h-[50%] flex gap-[0.25vw]">
              {
                prices.map((price) =>
                  <button
                    key={price}
                    style={
                      {
                        "--bg-color": COLOR_UI_INFO[trade_chore.player_2].lightColorCode,
                      } as React.CSSProperties
                    }
                    className="flex-1 whitespace-nowrap bg-(--bg-color) rounded-lg p-[0.25vw] text-[2.5cqw] disabled:text-white"
                    onClick={() => tradeFunc({ money_2: price })}
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
            <div className="text-[3cqw] font-bold">{formatBudget(trade_chore.player_2_item.total)}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function RuleTab(props: GameBoardProps & { setRuleEnabled: (_: boolean) => void }) {
  const { gameData, setRuleEnabled } = props;
  const buttonClassName = "px-[4cqw] rounded disabled:text-white disabled:bg-gray-300 border-2 border-white";
  const rule = gameData.rule;
  return (
    <div className="w-full h-full flex flex-col gap-[1.5vw]">
      <div className="w-full h-[80%] flex flex-col text-white overflow-auto">
        {
          rule.split("\n").map(
            (line, idx) => <span key={idx}>{line}</span>
          )
        }
      </div>
      <div className="w-full flex justify-evenly px-[1.5vw] gap-[1.5vw] text-[2cqw]">
        <button
          className={buttonClassName + " bg-blue-300"}
          onClick={() => {
            setRuleEnabled(false);
          }}
        >Trở về
        </button>
      </div>
    </div>
  );
}

export function TradeTab(props: GameBoardProps) {
  const { gameState } = props;

  const start_trade_chore = gameState.current_chore.start_trade;
  const trade_chore = gameState.current_chore.trade;
  const [ruleEnabled, setRuleEnabled] = useState<boolean>(false);
  return (
    <div className="@container w-full h-full flex flex-col gap-[5vw]">
      <div className="w-full h-full flex">
        {
          start_trade_chore != null ?
            <SelectPlayerTab {...props} />
            :
            trade_chore != null ?
              <TradingTab {...props} />
              :
              ruleEnabled ?
                <RuleTab {...{ ...props, setRuleEnabled }} />
                :
                <NormalTradeTab {...{ ...props, setRuleEnabled }} />
        }
      </div>
    </div>
  );
}

