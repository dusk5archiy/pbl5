'use client'

import { GameBoardProps } from "./props";
import { ActionCardChore } from "@/app/model/chore";

interface ActionCardModalProps extends GameBoardProps {
  chore?: ActionCardChore;
}

export function ActionCardModal(props: ActionCardModalProps) {
  const { gameData, selectedActionGroup, selectedActionCard, chore } = props;
  let name = "";
  let content = "";
  let foot = "";
  if (chore != null) {
    const { group, card } = chore;
    ({ name, content, foot } = gameData.action_card[group][card]);
  } else {
    const info = gameData.action_card[selectedActionGroup][selectedActionCard];
    ({ name, content, foot } = info);
  }

  return (
    <div className="w-full h-full flex flex-col gap-[1.5vw] p-[1vw]">
      <div className="w-full flex justify-center font-bold text-[4cqw]">{name}</div>
      <div className="w-full flex flex-col">
        {
          content.split("\n").map(
            (line, idx) =>
              <div key={idx} className="w-full flex text-[4cqw]">{line}</div>
          )
        }
        {
          foot.split("\n").map(
            (line, idx) =>
              <div key={idx} className="w-full flex justify-center text-[4cqw] font-bold">{line}</div>
          )
        }
      </div>
    </div>
  );
}



