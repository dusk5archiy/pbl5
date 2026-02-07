import { PropertyTab } from "./PropertyTab";
import { GameBoardProps } from "./props";
import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { ActionCardTab } from "./ActionCardTab";
import { TradeTab } from "./TradeTab";
import { StatTab } from "./StatTab";

export function HandPanel(props: GameBoardProps) {
  const { gameState, propertyTab, setPropertyTab, setBdsShown } = props;
  const BUTTON_CLASS = "w-max h-max px-[2vw] py-[2vh] text-[2vw] px-[3vw] font-bold disabled:bg-(--bg-color) rounded bg-[lightgray] disabled:active:bg-(--bg-color)";
  return (
    <div className="w-full h-full flex flex-col gap-[2%] overflow-hidden">
      <div className="w-full h-[10%] flex justify-center gap-[0.5vw]">
        <button
          style={
            {
              '--bg-color': COLOR_UI_INFO[gameState.logic.viewing_player || gameState.logic.current_player].lightColorCode
            } as React.CSSProperties
          }
          className={BUTTON_CLASS}
          onClick={() => setBdsShown(0)}
        >Trở về
        </button>
        <button
          style={
            {
              '--bg-color': COLOR_UI_INFO[gameState.logic.viewing_player || gameState.logic.current_player].lightColorCode
            } as React.CSSProperties
          }
          className={BUTTON_CLASS}
          disabled={propertyTab == 0}
          onClick={() => setPropertyTab(0)}
        >BĐS
        </button>
        <button
          style={
            {
              '--bg-color': COLOR_UI_INFO[gameState.logic.viewing_player || gameState.logic.current_player].lightColorCode
            } as React.CSSProperties
          }
          className={BUTTON_CLASS}
          disabled={propertyTab == 1}
          onClick={() => setPropertyTab(1)}
        >Thẻ
        </button>
        <button
          style={
            {
              '--bg-color': COLOR_UI_INFO[gameState.logic.viewing_player || gameState.logic.current_player].lightColorCode
            } as React.CSSProperties
          }
          className={BUTTON_CLASS}
          disabled={propertyTab == 3}
          onClick={() => setPropertyTab(3)}
        >Thống kê
        </button>
        <button
          style={
            {
              '--bg-color': COLOR_UI_INFO[gameState.logic.viewing_player || gameState.logic.current_player].lightColorCode
            } as React.CSSProperties
          }
          className={BUTTON_CLASS}
          disabled={propertyTab == 2}
          onClick={() => setPropertyTab(2)}
        >Khác
        </button>
      </div>
      <div className="w-full h-[90%] flex overflow-auto">
        {
          propertyTab == 0 ?
            <PropertyTab {...props} /> :
            propertyTab == 1 ?
              <ActionCardTab {...props} /> :
              propertyTab == 2 ?
                <TradeTab {...props} /> :
                propertyTab == 3 ?
                  <StatTab {...props} /> :
                  undefined
        }
      </div>
    </div>
  );
}
