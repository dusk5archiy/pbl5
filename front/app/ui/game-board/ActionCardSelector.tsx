import { GameBoardProps } from "./props";
import { COLOR_UI_INFO } from "@/app/utils/pallete";

export function ActionCardSelector(props: GameBoardProps) {
  const {
    gameState, gameData,
    selectedActionGroup, setSelectedActionGroup,
    selectedActionCard, setSelectedActionCard,
    guest,
  } = props;
  const selector_class_name = "flex-1 max-h-full flex flex-col w-[23%] overflow-y-auto gap-[0.5vw] pr-[0.25vw]";
  const option_class_name = "w-full flex justify-center rounded whitespace-nowrap text-[5cqw] active:bg-gray-400 py-[2vw]";
  const ui_player = guest || gameState.logic.viewing_player;
  const active_color = COLOR_UI_INFO[ui_player].lightColorCode;
  const inactive_color = "lightgray";

  const selectGroup = (group: string) => {
    const card = Object.keys(gameState.logic.action[group])[0]
    setSelectedActionGroup(group);
    setSelectedActionCard(card)
  };

  return (
    <div className="@container w-full h-full flex items-center gap-[0.5vw]" id="bds-selector">
      <div className={selector_class_name}>
        {
          Object.keys(gameState.logic.action[selectedActionGroup]).map(
            (card) => (
              <button key={card}
                style={
                  {
                    "--bg-color": selectedActionCard == card ? active_color : inactive_color,
                  } as React.CSSProperties
                }
                className={option_class_name + " bg-(--bg-color)"}
                onClick={() => setSelectedActionCard(card)}
              >{card}
              </button>
            )
          )
        }
      </div>
      <div className={selector_class_name}>
        {
          Object.keys(gameState.logic.action).map(
            (group) => (
              <button key={group}
                style={
                  {
                    "--bg-color": selectedActionGroup == group ? active_color : inactive_color,
                  } as React.CSSProperties
                }
                className={option_class_name + " bg-(--bg-color)"}
                onClick={() => selectGroup(group)}
              >{gameData.action_name[group]}
              </button>
            )
          )
        }
      </div>
    </div>
  );
}

