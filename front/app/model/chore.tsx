// ----------------------------------------------------------------------------

interface BaseChore {
  then?: Chore;
}

export interface BuyChore extends BaseChore {
  player: string;
  bds: string;
  price: number;
}

export interface PayChore extends BaseChore {
  player: string;
  receiver?: string;
  amount: number;
  bds?: string;
}

export interface AuctionBdsChore extends BaseChore {
  original_price: number;
  bds: string;
}

export interface AuctionBdsCurrentChore extends AuctionBdsChore {
  players: string[];
  current_price: number;
  player: string;
}


// ----------------------------------------------------------------------------

export interface RollDiceChore extends BaseChore { }

export interface JailChore extends BaseChore {
  amount: number;
}

// ----------------------------------------------------------------------------

export interface DiceCChore extends BaseChore { }

export interface DiceXbChore extends BaseChore { }

export interface TripleDiceChore extends BaseChore { }

// ----------------------------------------------------------------------------

export interface ActionCardChore extends BaseChore {
  group: string;
  card: string;
}

interface TwoDiceRentUChore extends BaseChore {
  bds: string;
  player: string;
}

export interface ReceiveMortgageChore extends BaseChore {
  player: string;
  bds: string; unmortgage: number;
  interest: number;
}

// ----------------------------------------------------------------------------

interface EndTurnChore extends BaseChore {
  player: string;
  next_player: boolean;
}

export interface EndGameChore extends BaseChore {
  player_order: string[];
}

// ----------------------------------------------------------------------------

interface StartTradeChore {
  player: string;
  players: string[];
}

export interface TradeCard {
  group: string;
  card: string;
}

interface TradeItem {
  bds: string[];
  card: TradeCard[];
  money: number;
  total: number;
}

export interface TradeChore extends BaseChore {
  player: string;
  player_1: string;
  player_2: string;
  player_1_item: TradeItem;
  player_2_item: TradeItem;
  confirm_mode: boolean;
}

// ----------------------------------------------------------------------------

export interface Chore {
  buy: BuyChore[];
  auction_bds: AuctionBdsChore[];
  auction_bds_current: AuctionBdsCurrentChore[];
  pay: PayChore[];
  two_dice_rent_u: TwoDiceRentUChore[];

  roll_dice: RollDiceChore[];
  jail: JailChore[];

  dice_c: DiceCChore[];
  dice_xb: DiceXbChore[];
  triple_dice: TripleDiceChore[];

  action_card: ActionCardChore[];
  receive_mortgage: ReceiveMortgageChore[];

  end_game: EndGameChore[];

  start_trade: StartTradeChore[];
  trade: TradeChore[];
}

// ----------------------------------------------------------------------------

export interface CurrentChore {
  buy?: BuyChore;
  pay?: PayChore;

  auction_bds?: AuctionBdsCurrentChore;

  dice_c?: DiceCChore;
  dice_xb?: DiceXbChore;
  triple_dice?: TripleDiceChore;

  roll_dice?: RollDiceChore;
  jail?: JailChore;
  two_dice_rent_u?: TwoDiceRentUChore;

  action_card?: ActionCardChore;
  end_turn?: EndTurnChore;

  receive_mortgage?: ReceiveMortgageChore;
  end_game?: EndGameChore;

  start_trade?: StartTradeChore;
  trade?: TradeChore;
}

// ----------------------------------------------------------------------------
