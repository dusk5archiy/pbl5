import { GameBoardProps } from "../game-board/props";
import { COLOR_UI_INFO } from "@/app/utils/pallete";

export function PropertySelector(props: GameBoardProps) {
  const {
    gameData,
    gameState,
    selectedBoard,
    selectedTrack,
    selectedGroup,
    selectedBds,
    setSelectedTrack,
    setSelectedBoard,
    setSelectedGroup,
    setSelectedBds,
    guest,
  } = props;

  const selector_class_name = "flex-1 max-h-full flex flex-col w-[23%] overflow-y-auto gap-[0.5vw] pr-[0.25vw]";
  const option_class_name = "w-full flex justify-center rounded whitespace-nowrap text-[5cqh] active:bg-gray-400 py-[2vw]";

  const player = gameState.logic.viewing_player;
  const ui_player = guest || player;

  const active_color = COLOR_UI_INFO[ui_player].lightColorCode;
  const inactive_color = "lightgray";

  const selectBoard = (board: number) => {
    const track = 0;
    const group = Object.keys(gameData.bds_selector[board][track])[0];
    const bds = gameData.bds_selector[board][track][group][0];
    setSelectedBoard(board);
    setSelectedTrack(track);
    setSelectedGroup(group);
    setSelectedBds(bds);
  };

  const selectTrack = (track: number) => {
    const group = Object.keys(gameData.bds_selector[selectedBoard][track])[0];
    const bds = gameData.bds_selector[selectedBoard][track][group][0];
    setSelectedTrack(track);
    setSelectedGroup(group);
    setSelectedBds(bds);
  };

  const selectGroup = (group: string) => {
    const bds = gameData.bds_selector[selectedBoard][selectedTrack][group][0];
    setSelectedGroup(group);
    setSelectedBds(bds)
  };

  return (
    <div className="@container w-full h-full flex items-center gap-[0.5vw] overflow-hidden">
      <div className={selector_class_name}>
        {
          gameData.bds_selector[selectedBoard][selectedTrack][selectedGroup].map(
            (bds) => {
              const owner = gameState.logic.bds[bds].owner;
              return (
                <button key={bds}
                  style={
                    {
                      "--bg-color": owner == null ? inactive_color : COLOR_UI_INFO[owner].lightColorCode,
                    } as React.CSSProperties
                  }
                  className={option_class_name + " bg-(--bg-color)" + (bds == selectedBds ? " underline font-bold" : "")}
                  onClick={() => setSelectedBds(bds)}
                >{bds}
                </button>
              );
            })
        }
      </div>
      <div className={selector_class_name}>
        {
          Object.keys(gameData.bds_selector[selectedBoard][selectedTrack]).map(
            (idx) => (
              <button key={idx}
                style={
                  {
                    "--bg-color": selectedGroup == idx ? active_color : inactive_color,
                  } as React.CSSProperties
                }
                className={option_class_name + " bg-(--bg-color)"}
                onClick={() => selectGroup(idx)}
              >{idx}
              </button>
            )
          )
        }
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
                className={option_class_name + " bg-(--bg-color)"}
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
                className={option_class_name + " bg-(--bg-color)"}
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
