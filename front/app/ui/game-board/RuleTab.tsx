import { GameBoardProps } from "./props";
export function RuleTab(props: GameBoardProps) {
  const { gameData } = props;
  const rule = gameData.rule;
  return (
    <div className="w-full h-full flex flex-col justify-center gap-[1.5vw]">
      <div className="w-full h-[80%] flex flex-col text-white overflow-auto">
        {
          rule.split("\n").map(
            (line, idx) => <span key={idx}>{line}</span>
          )
        }
      </div>
    </div>
  );
}


