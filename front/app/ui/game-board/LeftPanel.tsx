import { BudgetPanel } from "@/app/ui/game-board/BudgetPanel";
import { GameBoardProps } from "./props";
import { COLOR_UI_INFO } from "@/app/utils/pallete";

const COMMON_BUTTON_STYLE = " h-full text-[6cqw] font-bold text-gray-800 rounded active:bg-gray-300 disabled:text-white whitespace-nowrap overflow-hidden";

function RollDiceButton(
  props: GameBoardProps,
) {
  const { gameState, diceDetection, getDiceCaptureResults, sendRollDice } = props;
  const jail_chore = gameState.current_chore.jail;
  const roll_dice_chore = gameState.current_chore.roll_dice;
  const two_dice_rent_u_chore = gameState.current_chore.two_dice_rent_u;

  return (
    <button
      style={
        {
          '--bg-color': COLOR_UI_INFO[gameState.logic.current_player].lightColorCode
        } as React.CSSProperties
      }
      onClick={diceDetection ? () => getDiceCaptureResults() : () => sendRollDice({})}
      disabled={
        jail_chore == null &&
        roll_dice_chore == null &&
        two_dice_rent_u_chore == null
      }
      className={"w-full bg-(--bg-color) disabled:active:bg-(--bg-color)" + COMMON_BUTTON_STYLE}
    >Thảy
    </button>
  );
}

function BDSButton(props: GameBoardProps) {
  const { bdsShown, setBdsShown } = props;
  return (
    <button
      className={"w-full bg-gray-100" + COMMON_BUTTON_STYLE}
      onClick={() => setBdsShown((bdsShown + 1) % 2)}
    >BĐS
    </button>
  );
}

function NextButton(
  props: GameBoardProps,
) {
  const { gameState, diceCFunc, diceXbFunc, actionCardFunc, jailFunc } = props;
  const jail_chore = gameState.current_chore.jail;
  const dice_c_chore = gameState.current_chore.dice_c;
  const dice_xb_chore = gameState.current_chore.dice_xb;
  const action_card_chore = gameState.current_chore.action_card;
  return (
    <button
      style={
        {
          '--bg-color': COLOR_UI_INFO[gameState.logic.current_player].lightColorCode
        } as React.CSSProperties
      }
      disabled={
        jail_chore == null
        && dice_c_chore == null
        && dice_xb_chore == null
        && action_card_chore == null
      }
      onClick={
        jail_chore != null ? () => jailFunc({ response: 1 }) :
          dice_c_chore != null ? diceCFunc :
            dice_xb_chore != null ? diceXbFunc :
              action_card_chore != null ? actionCardFunc :
                undefined
      }
      className={"w-full bg-(--bg-color) disabled:active:bg-(--bg-color)" + COMMON_BUTTON_STYLE}
    >
      {
        jail_chore != null ? "Ra tù" : "Tiếp"
      }
    </button>
  );
}

function EndTurnButton(props: GameBoardProps) {
  const { gameState, endTurnFunc } = props;
  const end_turn_chore = gameState.current_chore.end_turn;
  return (
    <button
      style={
        {
          '--bg-color': COLOR_UI_INFO[gameState.logic.current_player].lightColorCode
        } as React.CSSProperties
      }
      onClick={endTurnFunc}
      disabled={end_turn_chore == null}
      className={"w-full bg-(--bg-color) disabled:active:bg-(--bg-color)" + COMMON_BUTTON_STYLE}
    >Kết
    </button>
  );
}

export function LeftPanel(props: GameBoardProps) {
  return (
    <div className="@container w-full h-full flex gap-[1vh]">
      <div className="w-[50%] h-full flex">
        <BudgetPanel {...props} />
      </div>
      <div className="w-[50%] h-full flex flex-col gap-[0.5vw] justify-between">
        <div className="flex-1 flex gap-[0.5vw]">
          <div className="flex flex-1">
            <RollDiceButton {...props} />
          </div>
          <div className="flex flex-1">
            <BDSButton {...props} />
          </div>
        </div>
        <div className="flex-1 flex gap-[0.5vw]">
          <div className="flex flex-1">
            <NextButton {...props} />
          </div>
          <div className="flex flex-1">
            <EndTurnButton {...props} />
          </div>
        </div>
      </div>
    </div>
  );
}
