import { BudgetPanel } from "@/app/ui/game-board/BudgetPanel";
import { GameBoardProps } from "./props";
import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { formatBudget } from "@/app/utils/format";

const COMMON_BUTTON_STYLE = " h-full text-[6cqw] font-bold text-gray-800 rounded active:bg-gray-300 disabled:text-white whitespace-nowrap overflow-hidden";

function RollDiceButton(
  props: GameBoardProps & { color: string },
) {
  const { gameState, diceDetection, sendRollDice, color, guest } = props;
  const { jail, roll_dice, two_dice_rent_u } = gameState.current_chore;
  const can_interact = guest == null || guest == gameState.logic.viewing_player;

  return (
    <button
      style={
        {
          '--bg-color': color
        } as React.CSSProperties
      }
      onClick={diceDetection ? undefined : () => sendRollDice()}
      disabled={
        !can_interact ||
        (
          jail == null &&
          roll_dice == null &&
          two_dice_rent_u == null
        )
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
      onClick={() => { setBdsShown((bdsShown + 1) % 2); }}
    >Túi
    </button>
  );
}

function NextButton(
  props: GameBoardProps & { color: string, can_interact: boolean },
) {
  const { gameState, diceCFunc, diceXbFunc, actionCardFunc, jailFunc, color, can_interact } = props;
  const jail_chore = gameState.current_chore.jail;
  const dice_c_chore = gameState.current_chore.dice_c;
  const dice_xb_chore = gameState.current_chore.dice_xb;
  const action_card_chore = gameState.current_chore.action_card;
  return (
    <button
      style={
        {
          '--bg-color': color,
        } as React.CSSProperties
      }
      disabled={
        !can_interact || (
          jail_chore == null
          && dice_c_chore == null
          && dice_xb_chore == null
          && action_card_chore == null
        )
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
        jail_chore != null ? `-${formatBudget(jail_chore.amount)}` : "Tiếp"
      }
    </button>
  );
}

function EndTurnButton(props: GameBoardProps & { color: string, can_interact: boolean }) {
  const { gameState, endTurnFunc, color, can_interact } = props;
  const end_turn_chore = gameState.current_chore.end_turn;
  return (
    <button
      style={
        {
          '--bg-color': color
        } as React.CSSProperties
      }
      onClick={endTurnFunc}
      disabled={!can_interact || end_turn_chore == null}
      className={"w-full bg-(--bg-color) disabled:active:bg-(--bg-color)" + COMMON_BUTTON_STYLE}
    >Kết
    </button>
  );
}

export function LeftPanel(props: GameBoardProps) {
  const { guest, gameState } = props;
  const current_player = gameState.logic.current_player
  const color = COLOR_UI_INFO[guest || current_player].lightColorCode;
  const can_interact = guest == null || guest == current_player;
  return (
    <div className="@container w-full h-full flex gap-[1vh]">
      <div className="w-[50%] h-full flex">
        <BudgetPanel {...props} />
      </div>
      <div className="h-full flex flex-1 flex-col gap-[0.5vw] justify-between">
        {
          guest == null &&
          <div className="flex-1 flex gap-[0.5vw]">
            <div className="flex flex-1">
              <RollDiceButton {...{ ...props, color }} />
            </div>
            <div className="flex flex-1">
              <BDSButton {...props} />
            </div>
          </div>
        }
        <div className="h-[50%] flex gap-[0.5vw]">
          {
            guest != null &&
            <>
              <div className="flex flex-1">
                <RollDiceButton {...{ ...props, color }} />
              </div>
              <div className="flex flex-1">
                <BDSButton {...props} />
              </div>
            </>
          }
          <div className="flex flex-1">
            <NextButton {...{ ...props, color, can_interact }} />
          </div>
          <div className="flex flex-1">
            <EndTurnButton {...{ ...props, color, can_interact }} />
          </div>
        </div>
      </div>
    </div>
  );
}
