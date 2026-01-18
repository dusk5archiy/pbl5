from pydantic import BaseModel

# Models for Game State -------------------------------------------------------


class GameStatePlayer(BaseModel):
    budget: int
    at: str


class GameStateBDS(BaseModel):
    owner: str
    level: int


class GameState(BaseModel):
    kv_queue: list[str]
    ch_queue: list[str]
    bds: dict[str, GameStateBDS]
    cards: dict[str, str]
    player_queue: list[str]
    players: dict[str, GameStatePlayer]
    current_player: str
    double_roll_stack: int


# Models for Cards ------------------------------------------------------------


class Card(BaseModel):
    id: str
    title: str
    content: str


# Models for Properties -------------------------------------------------------


class BDS(BaseModel):
    id: str
    group: str
    name: str
    price: int
    rent: list[int]
    mortgage: int
    upgrade: int = 0


# -----------------------------------------------------------------------------
