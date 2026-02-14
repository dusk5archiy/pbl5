import { formatBudget } from "@/app/utils/format";
import { GameBoardProps } from "./props";

export default function DashTab(props: GameBoardProps) {
  const { gameState } = props;
  const pool = gameState.logic.budget["pool"];
  return (
    <div className="w-full h-full flex">
      <div className="w-full h-[15vh] flex">
        {
          pool != null &&
          <div className="w-[33%] h-full flex flex-col justify-center py-[1vw] px-[4vw] border-2 border-white text-white rounded overflow-hidden">
            <div className={`w-full flex justify-center text-[3vh]`}>Kho</div>
            <div className={`w-full flex justify-center font-bold text-[4vh]`}>
              {formatBudget(pool)}
            </div>
          </div>
        }
      </div>
    </div>
  );
}
