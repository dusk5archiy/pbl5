import { GameBoardProps } from "./props";
import { DiceDock } from "./DiceDock";
import { BuyModal } from "./BuyModal";
import { AuctionModal } from "./AuctionModal";
import { PayModal } from "./PayModal";
import { ReceiveMortgageModal } from "./ReceiveMortgageModal";
import { EndGamePanel } from "./EndGamePanel";
import { TripleDiceModal } from "./TripleDiceModal";
import { ActionCardModal } from "./ActionCardModal";
import { TradeModal } from "./TradeModal";
import { GameCamera } from "./GameCamera";

export function PromptModal(props: GameBoardProps) {
  const {
    gameState, buyFunc, auctionFunc, payFunc,
    receiveMortgageFunc, tradeFunc, diceDetection
  } = props;

  const roll_dice_chore = gameState.current_chore.roll_dice;
  const jail_chore = gameState.current_chore.jail;
  const two_dice_rent_u = gameState.current_chore.two_dice_rent_u;

  const buy_chore = gameState.current_chore.buy;

  return (
    <div className="w-full h-full flex flex-col">
      <div className="w-full h-[25%] flex">
        <DiceDock {...props} />
      </div>
      <div className="@container w-full h-[75%] flex rounded bg-emerald-200">
        {(roll_dice_chore != null || jail_chore != null || two_dice_rent_u != null) && diceDetection && <GameCamera {...props} />}
        {buy_chore != null && <BuyModal {...{ ...props, func: buyFunc, chore: buy_chore }} />}
        {gameState.current_chore.auction_bds != null && <AuctionModal {...{ ...props, func: auctionFunc, chore: gameState.current_chore.auction_bds }} />}
        {gameState.current_chore.pay != null && <PayModal {...{ ...props, func: payFunc, chore: gameState.current_chore.pay }} />}
        {gameState.current_chore.receive_mortgage != null && <ReceiveMortgageModal {...{ ...props, func: receiveMortgageFunc, chore: gameState.current_chore.receive_mortgage }} />}
        {gameState.current_chore.end_game != null && <EndGamePanel {...{ ...props, chore: gameState.current_chore.end_game }} />}
        {gameState.current_chore.triple_dice != null && <TripleDiceModal />}
        {gameState.current_chore.action_card != null && <ActionCardModal {...{ ...props, chore: gameState.current_chore.action_card }} />}
        {gameState.current_chore.trade != null && <TradeModal {...{ ...props, func: tradeFunc, chore: gameState.current_chore.trade }} />}
      </div>
    </div>
  );
}
