from pydantic import BaseModel

# -----------------------------------------------------------------------------


class Space(BaseModel):
    orient: str
    x: float
    y: float


class Board(BaseModel):
    SE: str
    S: list[str]
    SW: str
    W: list[str]
    NW: str
    N: list[str]
    NE: str
    E: list[str]
    special_groups: dict[str, list[str]]

    def space(self):
        vt_max = len(self.S) + 4
        return (
            {
                space: Space(orient="S", x=vt_max - 3 - i, y=vt_max - 2)
                for i, space in enumerate(self.S)
            }
            | {
                space: Space(orient="W", x=0, y=vt_max - 3 - i)
                for i, space in enumerate(self.W)
            }
            | {
                space: Space(orient="E", x=vt_max - 2, y=2 + i)
                for i, space in enumerate(self.E)
            }
            | {space: Space(orient="N", x=2 + i, y=0) for i, space in enumerate(self.N)}
            | {
                self.SE: Space(orient="SE", x=vt_max - 2, y=vt_max - 2),
                self.SW: Space(orient="SW", x=0, y=vt_max - 2),
                self.NW: Space(orient="NW", x=0, y=0),
                self.NE: Space(orient="NE", x=vt_max - 2, y=0),
            }
            | {"OT": Space(orient="SW", x=0.75, y=vt_max - 2)}
        )

    def track(self):
        return [self.SE, *self.S, self.SW, *self.W, self.NW, *self.N, self.NE, *self.E]

    def special_spaces(self):
        return {
            space: group
            for group, spaces in self.special_groups.items()
            for space in spaces
        }


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
    title: str
    content: str


# Models for Properties -------------------------------------------------------


class BDS(BaseModel):
    group: str
    name: str
    price: int
    rent: list[int]
    mortgage: int
    upgrade: int = 0


# -----------------------------------------------------------------------------


class ColorPallete(BaseModel):
    groups: dict[str, str]
    border: str
    spaces: dict[str, str]
    cards: dict[str, str]
    players: dict[str, str]
    circle: dict[str, str]


# -----------------------------------------------------------------------------


class GameData(BaseModel):
    vt_max: int
    kv: dict[str, Card]
    ch: dict[str, Card]
    bds: dict[str, BDS]
    space: dict[str, Space]
    track: list[str]
    color_pallete: ColorPallete
    space_labels: dict[str, str]
    special_spaces: dict[str, str]


# -----------------------------------------------------------------------------
