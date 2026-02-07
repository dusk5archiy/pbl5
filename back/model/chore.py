from pydantic import BaseModel

# -----------------------------------------------------------------------------


class Chore(BaseModel):
    get_out_of_jail: list["GetOutOfJailChore"] = []
    move_steps: list["MoveStepsChore"] = []

    buy: list["BuyChore"] = []
    auction_bds: list["AuctionBdsChore"] = []
    auction_bds_current: list["AuctionBdsCurrentChore"] = []

    pay: list["PayChore"] = []
    two_dice_rent_u: list["TwoDiceRentUChore"] = []

    roll_dice: list["RollDiceChore"] = []
    jail: list["JailChore"] = []

    dice_c: list["DiceCChore"] = []
    dice_xb: list["DiceXbChore"] = []
    triple_dice: list["TripleDiceChore"] = []

    action_card: list["ActionCardChore"] = []
    receive_mortgage: list["ReceiveMortgageChore"] = []

    start_trade: list["StartTradeChore"] = []
    trade: list["TradeChore"] = []

    end_game: list["EndGameChore"] = []


class CurrentChore(BaseModel):
    buy: "BuyChore | None" = None
    pay: "PayChore | None" = None

    auction_bds: "AuctionBdsCurrentChore | None" = None

    dice_c: "DiceCChore | None" = None
    dice_xb: "DiceXbChore | None" = None
    triple_dice: "TripleDiceChore | None" = None

    roll_dice: "RollDiceChore | None" = None
    jail: "JailChore | None" = None
    two_dice_rent_u: "TwoDiceRentUChore | None" = None

    action_card: "ActionCardChore | None" = None
    end_turn: "EndTurnChore | None" = None

    receive_mortgage: "ReceiveMortgageChore | None" = None
    start_trade: "StartTradeChore | None" = None
    trade: "TradeChore | None" = None
    end_game: "EndGameChore | None" = None


class BaseChore(BaseModel):
    then: Chore | None = None


class BuyChore(BaseChore):
    player: str
    bds: str
    price: int


class PayChore(BaseChore):
    player: str
    receiver: str | None
    amount: int
    bds: str | None = None


class AuctionBdsChore(BaseChore):
    original_price: int
    bds: str


class AuctionBdsCurrentChore(AuctionBdsChore):
    players: list[str]
    current_price: int
    player: str


# -----------------------------------------------------------------------------


class RollDiceChore(BaseChore):
    pass


class JailChore(BaseChore):
    amount: int


# -----------------------------------------------------------------------------


class DiceCChore(BaseChore):
    pass


class DiceXbChore(BaseChore):
    pass


class TripleDiceChore(BaseChore):
    pass


# -----------------------------------------------------------------------------


class ActionCardChore(BaseChore):
    group: str
    card: str


class TwoDiceRentUChore(BaseChore):
    bds: str
    player: str


class ReceiveMortgageChore(BaseChore):
    player: str
    bds: str
    unmortgage: int
    interest: int


class MoveStepsChore(BaseChore):
    player: str
    steps: int


# -----------------------------------------------------------------------------


class GetOutOfJailChore(BaseChore):
    player: str


# -----------------------------------------------------------------------------


class EndTurnChore(BaseChore):
    player: str
    next_player: bool


class EndGameChore(BaseChore):
    player_order: list[str]


# -----------------------------------------------------------------------------


class StartTradeChore(BaseChore):
    player: str
    players: list[str]


class TradeCard(BaseModel):
    group: str
    card: str

    def __eq__(self, other):
        return (
            isinstance(other, TradeCard)
            and self.group == other.group
            and self.card == other.card
        )


class TradeItem(BaseModel):
    bds: list[str] = []
    card: list[TradeCard] = []
    money: int = 0
    total: int = 0


class TradeChore(BaseChore):
    player: str
    player_1: str
    player_2: str
    player_1_item: TradeItem = TradeItem()
    player_2_item: TradeItem = TradeItem()
    confirm_mode: bool = False


# -----------------------------------------------------------------------------
