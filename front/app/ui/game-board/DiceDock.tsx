import { GameBoardProps } from "./props";
import { BOARD_BG_COLOR } from "@/app/utils/pallete";

function getDrawDiceFunction(props: GameBoardProps) {
  const { gameState } = props;
  const x = 4;
  const y = "2cqh";
  const width = 10;
  const size = width + 1;
  let i = 0;
  const { dice_1, dice_2, dice_3 } = gameState.effect;
  const double_stack = gameState.logic.player[gameState.logic.current_player].double_stack;
  return () => (
    <g>
      {dice_1 && <image x={`${x + (i++) * size}cqw`} y={y} height={`${width}cqw`} href={`/assets/dice/dice${dice_1}.svg`} />}
      {dice_2 && <image x={`${x + (i++) * size}cqw`} y={y} height={`${width}cqw`} href={`/assets/dice/dice${dice_2}.svg`} />}
      {dice_3 && <image x={`${x + (i++) * size}cqw`} y={y} height={`${width}cqw`} href={`/assets/dice/dice-3${dice_3}.svg`} />}
      {dice_1 && double_stack > 0 && <image x={`${x + (i++) * size}cqw`} y={y} height={`${width}cqw`} href={`/assets/dice/sd${double_stack}.svg`} />}
    </g>
  );
}

export function DiceDock(props: GameBoardProps) {
  const drawDice = getDrawDiceFunction(props);
  return (
    <div className="@container w-full h-full flex">
      <svg width="100%" height="100%">
        <rect x="0" y="0" width="100%" height="100%" rx="2%" fill={BOARD_BG_COLOR} strokeWidth="1" />
        {drawDice()}
      </svg>
    </div>
  );
}
