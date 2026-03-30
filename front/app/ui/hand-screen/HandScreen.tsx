import { PropertyTab } from "../property-tab/PropertyTab";
import { GameBoardProps } from "../game-board/props";
import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { ActionCardTab } from "../action-card-tab/ActionCardTab";
import { OtherTab } from "./OtherTab";
import { StatTab } from "./StatTab";
import { RuleTab } from "./RuleTab";
import { TradeTab } from "./TradeTab";

export function HandScreen(props: GameBoardProps) {
  const { gameState, propertyTab, setPropertyTab, setBdsShown, guest } = props;
  const ui_player = guest || gameState.logic.viewing_player;
  const color = COLOR_UI_INFO[ui_player].lightColorCode;
  const BUTTON_CLASS = "w-max h-max px-[2vw] py-[2vh] text-[2vw] px-[3vw] font-bold disabled:bg-(--bg-color) rounded bg-[lightgray] disabled:active:bg-(--bg-color)";

  return (
    <div className="w-full h-full flex flex-col gap-[2%] overflow-hidden">
      <div className="w-full h-[10%] flex gap-[0.5vw] overflow-x-auto overflow-y-hidden">
        <button
          style={
            {
              '--bg-color': color,
            } as React.CSSProperties
          }
          className={BUTTON_CLASS}
          onClick={() => setBdsShown(0)}
        >Trở về
        </button>
        <button
          style={
            {
              '--bg-color': color,
            } as React.CSSProperties
          }
          className={BUTTON_CLASS}
          disabled={propertyTab == "bds"}
          onClick={() => setPropertyTab("bds")}
        >BĐS
        </button>
        <button
          style={
            {
              '--bg-color': color,
            } as React.CSSProperties
          }
          className={BUTTON_CLASS}
          disabled={propertyTab == "action_card"}
          onClick={() => setPropertyTab("action_card")}
        >Thẻ
        </button>
        <button
          style={
            {
              '--bg-color': color,
            } as React.CSSProperties
          }
          className={BUTTON_CLASS}
          disabled={propertyTab == "bds_stats"}
          onClick={() => setPropertyTab("bds_stats")}
        >Thống kê BĐS
        </button>
        <button
          style={
            {
              '--bg-color': color,
            } as React.CSSProperties
          }
          className={BUTTON_CLASS}
          disabled={propertyTab == "trade"}
          onClick={() => setPropertyTab("trade")}
        >Trao đổi
        </button>
        <button
          style={
            {
              '--bg-color': color,
            } as React.CSSProperties
          }
          className={BUTTON_CLASS}
          disabled={propertyTab == "other"}
          onClick={() => setPropertyTab("other")}
        >Khác
        </button>
        <button
          style={
            {
              '--bg-color': color,
            } as React.CSSProperties
          }
          className={BUTTON_CLASS}
          disabled={propertyTab == "rule"}
          onClick={() => setPropertyTab("rule")}
        >Luật chơi
        </button>
      </div>
      <div className="w-full h-[90%] flex overflow-auto">
        {
          propertyTab == "bds" ?
            <PropertyTab {...props} /> :
            propertyTab == "action_card" ?
              <ActionCardTab {...props} /> :
              propertyTab == "bds_stats" ?
                <StatTab {...props} /> :
                propertyTab == "rule" ?
                  <RuleTab {...props} /> :
                  propertyTab == "trade" ?
                    <TradeTab {...props} /> :
                    propertyTab == "other" ?
                      <OtherTab {...props} /> :
                      null
        }
      </div>
    </div>
  );
}
