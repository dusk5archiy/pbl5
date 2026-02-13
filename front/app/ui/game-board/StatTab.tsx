import { GameBoardProps } from "./props";
import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { formatBudget } from "@/app/utils/format";

export function StatTab(props: GameBoardProps) {
  const {
    gameData,
    gameState,
    selectedBoard,
    selectedTrack,
    focusBds,
    setPropertyTab
  } = props;

  const selector_class_name = "flex-1 max-h-full flex flex-col overflow-auto gap-[0.5vw] pr-[0.25vw]";
  const selector_class_name_2 = "flex-1 flex w-full h-[5vh] gap-[0.5vw] pr-[0.25vw]";
  const option_class_name = "w-full flex justify-evenly rounded text-[3cqh] active:bg-gray-400";
  const option_class_name_2 = option_class_name + " py-[1vw] text-[3cqw]";
  const active_color = COLOR_UI_INFO[gameState.logic.viewing_player || gameState.logic.current_player].lightColorCode;
  const inactive_color = "lightgray";

  const selectBoard = (board: number) => {
    const track = 0;
    const group = Object.keys(gameData.bds_selector[board][track])[0];
    const bds = gameData.bds_selector[board][track][group][0];
    focusBds(bds);
  };

  const selectTrack = (track: number) => {
    const group = Object.keys(gameData.bds_selector[selectedBoard][track])[0];
    const bds = gameData.bds_selector[selectedBoard][track][group][0];
    focusBds(bds);
  };

  return (
    <div className="@container w-full h-full flex items-center gap-[0.5vw] overflow-hidden" id="bds-selector">
      <div className={"flex-2 max-h-full flex w-[50%] overflow-auto"}>
        <div className={"flex flex-col w-full h-full gap-[0.5vw] pr-[0.25vw]"}>
          {
            Object.keys(gameData.bds_selector[selectedBoard][selectedTrack]).map(
              (group) => (
                <div key={group} className={selector_class_name_2}>
                  {
                    gameData.bds_selector[selectedBoard][selectedTrack][group].map(
                      (bds) => {

                        const price = gameData.bds[bds].price;
                        let text = `${bds}\n${formatBudget(price)}`;
                        const owner = gameState.logic.bds[bds].owner;
                        const level = gameState.ui.bds[bds].level;
                        if (level != null && owner != null) {
                          text = `${bds}\nLv.${level >= 0 ? level : "-"}`;
                        }
                        return (
                          <button key={bds}
                            style={
                              {
                                "--bg-color": gameState.logic.bds[bds].owner != null ? COLOR_UI_INFO[gameState.logic.bds[bds].owner].lightColorCode : inactive_color
                              } as React.CSSProperties
                            }
                            className={option_class_name + " bg-(--bg-color)"}
                            onClick={() => {
                              focusBds(bds);
                              setPropertyTab(0);
                            }}
                          >{text.split("\n").map(
                            (line, i) => <span key={i}>{line}</span>
                          )}
                          </button>
                        )
                      }
                    )
                  }
                </div>
              )
            )
          }
        </div>
      </div>
      <div className={selector_class_name}>
        {
          gameData.bds_selector[selectedBoard].map(
            (_, idx) => (
              <button key={idx}
                style={
                  {
                    "--bg-color": selectedTrack == idx ? active_color : inactive_color,
                  } as React.CSSProperties
                }
                className={option_class_name_2 + " bg-(--bg-color)"}
                onClick={() => selectTrack(idx)}
              >Tầng {idx + 1}
              </button>
            )
          )
        }
      </div>
      <div className={selector_class_name}>
        {
          gameData.bds_selector.map(
            (_, idx) => (
              <button key={idx}
                style={
                  {
                    "--bg-color": selectedBoard == idx ? active_color : inactive_color,
                  } as React.CSSProperties
                }
                className={option_class_name_2 + " bg-(--bg-color)"}
                onClick={() => selectBoard(idx)}
              >Bàn {idx + 1}
              </button>
            )
          )
        }
      </div>
    </div>
  );
}
