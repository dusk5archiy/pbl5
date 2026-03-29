from pydantic import BaseModel
from model.chore import Chore, CurrentChore

# -----------------------------------------------------------------------------


class LogicStatePlayer(BaseModel):
    at: str
    double_stack: int = 0
    jail_stack: int = 0
    alive: bool = True


class LogicStateBDS(BaseModel):
    owner: str | None = None
    level: int = 0


class LogicStateBuild(BaseModel):
    house: int
    hotel: int
    skyscraper: int


class LogicStateAction(BaseModel):
    owner: str | None = None


# -----------------------------------------------------------------------------


class GameLogicState(BaseModel):
    bds: dict[str, LogicStateBDS]
    player: dict[str, LogicStatePlayer]
    player_order: list[str]
    current_player: str
    viewing_player: str
    build: LogicStateBuild
    action_card: dict[str, list[str]]
    rent_multiplier: int = 1
    u_multiplier: int | None = None
    steps: int | None = None
    action: dict[str, dict[str, LogicStateAction]]
    budget: dict[str, int]


# -----------------------------------------------------------------------------


class UiStatePlayer(BaseModel):
    total: int = 0

    @classmethod
    def new(cls, logic: GameLogicState, player: str):
        logic, player = logic, player
        return UiStatePlayer(total=0)


class UiStateBDS(BaseModel):
    level: int = 0
    can_upgrade: bool = False
    can_downgrade: bool = False
    can_mortgage: bool = False
    can_unmortgage: bool = False
    upgrade_amount: int | None = None
    downgrade_amount: int | None = None
    mortgage_amount: int | None = None
    unmortgage_amount: int | None = None
    can_choose: bool = False


class UiStateAction(BaseModel):
    can_use: bool = False
    can_choose: bool = False


# -----------------------------------------------------------------------------


class GameUiState(BaseModel):
    bds: dict[str, UiStateBDS]
    player: dict[str, UiStatePlayer]
    action: dict[str, dict[str, UiStateAction]]

    @classmethod
    def new(cls, logic: GameLogicState):
        ui = GameUiState(
            bds={bds: UiStateBDS() for bds in logic.bds.keys()},
            player={player: UiStatePlayer() for player in logic.player},
            action={
                group: {card_id: UiStateAction() for card_id in logic.action[group]}
                for group in logic.action
            },
        )
        return ui


# -----------------------------------------------------------------------------


class MovementLine(BaseModel):
    arrow: bool
    start: str
    end: str


# -----------------------------------------------------------------------------


class GameEffectState(BaseModel):
    bds_enabled: bool = True
    can_trade: bool = False
    wait_ms: int = 0
    select_bds: str | None = None
    movement_lines: list[MovementLine] = []
    dice_1: str | None = None
    dice_2: str | None = None
    dice_3: str | None = None
    board: int | None = None


# -----------------------------------------------------------------------------


class GameState(BaseModel):
    version: str
    turns: int = 0
    logic: GameLogicState
    ui: GameUiState
    effect: GameEffectState
    chore: Chore = Chore()
    current_chore: CurrentChore = CurrentChore()


# -----------------------------------------------------------------------------

TaskResult = tuple[GameState, "Task | None"]


class Task(BaseModel):
    def __call__(self, game_state: GameState) -> TaskResult:
        return game_state, None


# -----------------------------------------------------------------------------
