'use client'

import { GameBoardProps } from "./props";

export function TripleDiceModal(props: GameBoardProps) {
  const { gameState, guest } = props;
  if (guest != null && guest != gameState.logic.viewing_player) {
    return undefined;
  }
  let text = "Chọn ô bất kì và di chuyển tới đó.";

  return (
    <div className="w-full h-full flex flex-col gap-[1.5vw] justify-center">
      <div className="w-full flex justify-center font-bold whitespace-nowrap text-[4cqw]">{text}</div>
    </div>
  );
}


