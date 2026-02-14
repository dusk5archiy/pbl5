from pydantic import BaseModel

# -----------------------------------------------------------------------------


class TrackBorder(BaseModel):
    top_left: int
    bottom_right: int


class Space(BaseModel):
    board: int
    track: int
    orient: str
    x: float
    y: float
    w: float
    h: float


# -----------------------------------------------------------------------------


class GameDataTrackModel(BaseModel):
    S: list[str]
    W: list[str]
    N: list[str]
    E: list[str]
    NW: str
    NE: str
    SW: str
    SE: str

    def space_id_list(self) -> list[str]:
        return [self.SE, *self.S, self.SW, *self.W, self.NW, *self.N, self.NE, *self.E]

    def size(self) -> int:
        return len(self.S) + 4

    def track_border(self, board_size: int, track_index: int):
        return TrackBorder(
            top_left=2 * track_index, bottom_right=board_size - 2 * track_index
        )

    def path(self):
        return (
            {
                self.SE: self.S[0],
                self.SW: self.W[0],
                self.NW: self.N[0],
                self.NE: self.E[0],
            }
            | {
                track[i]: track[i + 1]
                for track in [self.S, self.W, self.N, self.E]
                for i in range(len(track) - 1)
            }
            | {
                self.S[-1]: self.SW,
                self.W[-1]: self.NW,
                self.N[-1]: self.NE,
                self.E[-1]: self.SE,
            }
        )

    def space(self, board_index: int, track_index: int):
        global_offset = 2 * track_index
        track_size = self.size()
        return (
            {
                space: Space(
                    board=board_index,
                    track=track_index,
                    orient="S",
                    x=global_offset + track_size - 3 - i,
                    y=global_offset + track_size - 2,
                    w=1,
                    h=2,
                )
                for i, space in enumerate(self.S)
            }
            | {
                space: Space(
                    board=board_index,
                    track=track_index,
                    orient="W",
                    x=global_offset,
                    y=global_offset + track_size - 3 - i,
                    w=2,
                    h=1,
                )
                for i, space in enumerate(self.W)
            }
            | {
                space: Space(
                    board=board_index,
                    track=track_index,
                    orient="E",
                    x=global_offset + track_size - 2,
                    y=global_offset + 2 + i,
                    w=2,
                    h=1,
                )
                for i, space in enumerate(self.E)
            }
            | {
                space: Space(
                    board=board_index,
                    track=track_index,
                    orient="N",
                    x=global_offset + 2 + i,
                    y=global_offset,
                    w=1,
                    h=2,
                )
                for i, space in enumerate(self.N)
            }
            | {
                self.SE: Space(
                    board=board_index,
                    track=track_index,
                    orient="SE",
                    x=global_offset + track_size - 2,
                    y=global_offset + track_size - 2,
                    w=2,
                    h=2,
                ),
                self.SW: Space(
                    board=board_index,
                    track=track_index,
                    orient="SW",
                    x=global_offset,
                    y=global_offset + track_size - 2,
                    w=2,
                    h=2,
                ),
                self.NW: Space(
                    board=board_index,
                    track=track_index,
                    orient="NW",
                    x=global_offset,
                    y=global_offset,
                    w=2,
                    h=2,
                ),
                self.NE: Space(
                    board=board_index,
                    track=track_index,
                    orient="NE",
                    x=global_offset + track_size - 2,
                    y=global_offset,
                    w=2,
                    h=2,
                ),
            }
        )


# -----------------------------------------------------------------------------


class GameDataBoardModel(BaseModel):
    tracks: list[GameDataTrackModel]

    @property
    def num_tracks(self):
        return len(self.tracks)

    def size(self):
        return self.tracks[0].size()

    def track_border(self):
        return [
            track.track_border(self.size(), i) for i, track in enumerate(self.tracks)
        ]

    def space_id_list(self) -> list[str]:
        return [i for track in self.tracks for i in track.space_id_list()]

    def space(self, board_index: int):
        return {
            key: value
            for track_index, track in enumerate(self.tracks)
            for key, value in track.space(
                board_index=board_index, track_index=track_index
            ).items()
        }

    def path(self):
        return {
            key: value for track in self.tracks for key, value in track.path().items()
        }


# -----------------------------------------------------------------------------


class GameDataBoardSystemModel(BaseModel):
    boards: list[GameDataBoardModel]

    @property
    def num_boards(self):
        return len(self.boards)

    @property
    def num_tracks(self):
        return sum(board.num_tracks for board in self.boards)

    def size(self):
        return [board.size() for board in self.boards]

    def track_border(self):
        return [board.track_border() for board in self.boards]

    def space(self):
        return {
            key: value
            for board_index, board in enumerate(self.boards)
            for key, value in board.space(board_index=board_index).items()
        }

    def space_id_list(self) -> list[list[str]]:
        return [board.space_id_list() for board in self.boards]

    def path(self):
        return {
            key: value for board in self.boards for key, value in board.path().items()
        }

    def special_space(self):
        TT = self.space()["TT"]
        return {
            "OT": Space(
                board=TT.board,
                track=TT.track,
                orient="SW",
                x=TT.x + 0.75,
                y=TT.y,
                w=1.25,
                h=1.25,
            )
        }


# -----------------------------------------------------------------------------


class ActionSpaceInputModel(BaseModel):
    group: str
    near: str | None = None


class ActionCardInputModel(BaseModel):
    name: str
    content: str = ""
    foot: str = ""
    values: dict[str, str | int] | None = None
    collect: int | None = None
    pay: int | None = None
    pool: bool = False
    move: str | None = None
    copies: int = 1
    keep: bool = False


class ActionCard(BaseModel):
    name: str
    content: str
    foot: str


class ActionGroupInput(BaseModel):
    name: str
    cards: dict[str, ActionCardInputModel] = {}


class Action(BaseModel):
    name: str
    group: str


class ActionSystemModel(BaseModel):
    space: dict[str, ActionSpaceInputModel]
    group: dict[str, ActionGroupInput]
    label: dict[str, str]
    special_label: dict[str, str]

    def export_action_space(self):
        def f(action_id: str):
            action = self.space[action_id]
            group = self.group[action.group]
            return Action(
                name=group.name + f" ({action_id})"
                if action.near is None
                else f" ({action.near})",
                group=action.group,
            )

        return {spaceId: f(spaceId) for spaceId in self.space.keys()}

    def export_action_cards(self):
        return {group: self.group[group].cards for group in self.group}


# -----------------------------------------------------------------------------
