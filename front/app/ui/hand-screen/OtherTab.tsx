import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { GameBoardProps } from "../game-board/props";

function NormalTradeTab(props: GameBoardProps) {
  const {
    gameState,
    payFunc, receiveMortgageFunc, jailFunc, guest
  } = props;

  const can_interact = guest == null || guest == gameState.logic.viewing_player;

  const pay_chore = gameState.current_chore.pay;
  const receive_mortgage_chore = gameState.current_chore.receive_mortgage;
  const jail_chore = gameState.current_chore.jail;
  const ui_player = guest || gameState.logic.viewing_player;

  const BUTTON_CLASS = "w-max h-max px-[4cqw] py-[2cqw] text-[3cqw] font-bold bg-(--bg-color) rounded active:bg-[lightgray] disabled:text-white disabled:active:bg-(--bg-color)";
  const color = COLOR_UI_INFO[ui_player].lightColorCode;

  return (
    <div className="w-full h-full flex justify-center items-center gap-[1vw]">
      <button
        style={
          {
            '--bg-color': color,
          } as React.CSSProperties
        }
        onClick={
          pay_chore != null ?
            () => payFunc({ response: 0 }) :
            receive_mortgage_chore != null ?
              () => receiveMortgageFunc({ response: 0 }) :
              jail_chore != null ?
                () => jailFunc({ response: 0 }) :
                undefined
        }
        disabled={
          !can_interact ||
          (
            pay_chore == null
            && receive_mortgage_chore == null
            && jail_chore == null
          )
        }
        className={BUTTON_CLASS}
      >Phá sản
      </button>
    </div>
  );

}

export function OtherTab(props: GameBoardProps) {
  return (
    <div className="@container w-full h-full flex flex-col gap-[5vw]">
      <div className="w-full h-full flex">
        <NormalTradeTab {...props} />
      </div>
    </div>
  );
}

