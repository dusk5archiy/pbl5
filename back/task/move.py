from typing import Callable
from model.game_state import GameState, Task, TaskResult
from game_data_manager import GAME_DATA
from calc.calc import calc_new_space
from calc.mod import mod_move, mod_release, mod_intermediate
from case.case import CASE_LAND, CaseWrapper, CASE_PASS
from calc.switch import change_track_on_cau_condition, change_track_on_r_condition

# -----------------------------------------------------------------------------


class LandTask(Task):
    new_space: str
    player: str
    steps: int | None = None

    def __call__(self, game_state: GameState) -> TaskResult:
        FRONTEND_GAME_DATA = GAME_DATA[game_state.version].frontend_game_data
        cw = CaseWrapper(
            game_state=game_state,
            player=self.player,
            new_space=self.new_space,
            steps=self.steps,
            FRONTEND_GAME_DATA=FRONTEND_GAME_DATA,
        )
        for c in CASE_LAND:
            game_state, task, out = c(cw)
            if out:
                game_state.effect.wait_ms = 0
                return game_state, task

        return game_state, None


# -----------------------------------------------------------------------------


class MoveStepsTask(Task):
    player: str
    change_track_on_cau: bool
    change_track_on_r: bool
    steps_left: int
    reversed: bool = False

    @classmethod
    def from_steps(
        cls,
        player: str,
        steps: int,
        change_track: bool | None = None,
        change_track_on_cau: bool | None = None,
        change_track_on_r: bool | None = None,
        reversed: bool = False,
    ):
        task = MoveStepsTask(
            steps_left=steps,
            player=player,
            change_track_on_cau=change_track
            if change_track is not None
            else change_track_on_cau
            if change_track_on_cau is not None
            else change_track_on_cau_condition(steps),
            change_track_on_r=change_track
            if change_track is not None
            else change_track_on_r
            if change_track_on_r is not None
            else change_track_on_r_condition(steps),
            reversed=reversed,
        )

        return task

    @classmethod
    def prepare(cls, game_state: GameState) -> GameState:
        game_state.effect.movement_lines.clear()
        game_state = mod_move(game_state)
        game_state = mod_intermediate(game_state)
        return game_state

    def __call__(self, game_state: GameState) -> TaskResult:
        current_space = game_state.logic.player[self.player].at
        steps_left_next = self.steps_left - 1

        game_data = GAME_DATA[game_state.version]
        FRONTEND_GAME_DATA = game_data.frontend_game_data
        BACKEND_GAME_DATA = game_data.backend_game_data

        def check_last_space(_: str = ""):
            return steps_left_next == 0

        new_space = calc_new_space(
            game_state=game_state,
            current_space=current_space,
            FRONTEND_GAME_DATA=FRONTEND_GAME_DATA,
            BACKEND_GAME_DATA=BACKEND_GAME_DATA,
            check_last_space=check_last_space,
            change_track_on_cau=self.change_track_on_cau,
            change_track_on_r=self.change_track_on_r,
            draw_movement_lines=True,
            reversed=self.reversed,
        )

        new_board = FRONTEND_GAME_DATA.space[new_space].board
        game_state.logic.player[self.player].at = new_space
        game_state.effect.board = new_board

        cw = CaseWrapper(
            game_state=game_state,
            new_space=new_space,
            player=self.player,
            steps=game_state.logic.steps,
            FRONTEND_GAME_DATA=FRONTEND_GAME_DATA,
        )

        for c in CASE_PASS:
            game_state, task, out = c(cw)
            if out:
                return game_state, task

        if not check_last_space():
            task = MoveStepsTask(
                steps_left=steps_left_next,
                change_track_on_cau=self.change_track_on_cau,
                change_track_on_r=self.change_track_on_r,
                player=self.player,
                reversed=self.reversed,
            )
            game_state.effect.wait_ms = 100
            return game_state, task

        task = LandTask(
            new_space=new_space,
            player=self.player,
            steps=game_state.logic.steps,
        )
        game_state.effect.wait_ms = 200
        return game_state, task


# -----------------------------------------------------------------------------


class MoveNearestTask(Task):
    original_space: str
    change_track_on_cau: bool
    change_track_on_r: bool
    player: str
    check_last_space: Callable[[str], bool]
    reversed: bool = False

    @classmethod
    def create(
        cls,
        player: str,
        original_space: str,
        check_last_space: Callable[[str], bool],
        steps: int | None = None,
        change_track: bool | None = None,
        change_track_on_cau: bool | None = None,
        change_track_on_r: bool | None = None,
        reversed: bool = False,
    ):
        task = MoveNearestTask(
            player=player,
            check_last_space=check_last_space,
            original_space=original_space,
            change_track_on_cau=change_track
            if change_track is not None
            else change_track_on_cau
            if change_track_on_cau is not None
            else change_track_on_cau_condition(steps)
            if steps is not None
            else False,
            change_track_on_r=change_track
            if change_track is not None
            else change_track_on_r
            if change_track_on_r is not None
            else change_track_on_r_condition(steps)
            if steps is not None
            else False,
            reversed=reversed,
        )

        return task

    @classmethod
    def prepare(cls, game_state: GameState) -> GameState:
        game_state.effect.movement_lines.clear()
        game_state = mod_move(game_state)
        game_state = mod_intermediate(game_state)
        return game_state

    def __call__(self, game_state: GameState) -> TaskResult:
        current_space = game_state.logic.player[self.player].at

        game_data = GAME_DATA[game_state.version]
        FRONTEND_GAME_DATA = game_data.frontend_game_data
        BACKEND_GAME_DATA = game_data.backend_game_data

        def check_last_space(space: str):
            return space == self.original_space or self.check_last_space(space)

        new_space = calc_new_space(
            game_state=game_state,
            current_space=current_space,
            FRONTEND_GAME_DATA=FRONTEND_GAME_DATA,
            BACKEND_GAME_DATA=BACKEND_GAME_DATA,
            check_last_space=check_last_space,
            change_track_on_cau=self.change_track_on_cau,
            change_track_on_r=self.change_track_on_r,
            draw_movement_lines=True,
        )

        new_board = FRONTEND_GAME_DATA.space[new_space].board
        game_state.logic.player[self.player].at = new_space
        game_state.effect.board = new_board

        cw = CaseWrapper(
            FRONTEND_GAME_DATA=FRONTEND_GAME_DATA,
            game_state=game_state,
            new_space=new_space,
            player=self.player,
        )

        for c in CASE_PASS:
            game_state, task, out = c(cw)
            if out:
                return game_state, task

        if not self.check_last_space(new_space):
            task = MoveNearestTask(
                original_space=self.original_space,
                change_track_on_cau=self.change_track_on_cau,
                change_track_on_r=self.change_track_on_r,
                player=self.player,
                check_last_space=self.check_last_space,
                reversed=self.reversed,
            )
            game_state.effect.wait_ms = 100
            return game_state, task

        elif new_space == self.original_space:
            game_state, task = mod_release(game_state)
            return game_state, task

        task = LandTask(
            new_space=new_space,
            player=self.player,
            steps=game_state.logic.steps,
        )
        game_state.effect.wait_ms = 200
        return game_state, task


# -----------------------------------------------------------------------------


class MoveToSpaceTask(Task):
    destination: str
    player: str

    @classmethod
    def prepare(cls, game_state: GameState) -> GameState:
        game_state.effect.movement_lines.clear()
        game_state = mod_move(game_state)
        game_state = mod_intermediate(game_state)
        return game_state

    def __call__(self, game_state: GameState) -> TaskResult:
        game_data = GAME_DATA[game_state.version]
        FRONTEND_GAME_DATA = game_data.frontend_game_data
        BACKEND_GAME_DATA = game_data.backend_game_data
        current_space_id = game_state.logic.player[self.player].at
        current_space = FRONTEND_GAME_DATA.space[current_space_id]
        destination_space = FRONTEND_GAME_DATA.space[self.destination]

        current_track = (current_space.board, current_space.track)
        destination_track = destination_space.board, destination_space.track
        change_track_on_r = False
        for b in BACKEND_GAME_DATA.bds_group["R"].bds:
            if current_space_id == b:
                change_track_on_r = current_track < destination_track
            elif current_space_id == b + "A":
                change_track_on_r = current_track > destination_track

        change_track_on_cau = False
        if "CAU-1" in FRONTEND_GAME_DATA.space and "CAU-2" in FRONTEND_GAME_DATA.space:
            cau_1_space = FRONTEND_GAME_DATA.space["CAU-1"]
            cau_2_space = FRONTEND_GAME_DATA.space["CAU-2"]
            cau_1_track = (cau_1_space.board, cau_1_space.track)
            cau_2_track = (cau_2_space.board, cau_2_space.track)

            if current_space_id == "CAU-1":
                if cau_1_track < cau_2_track:
                    change_track_on_cau = current_track < destination_track
                elif cau_1_track > cau_2_track:
                    change_track_on_cau = current_track > destination_track
            elif current_space_id == "CAU-2":
                if cau_1_track < cau_2_track:
                    change_track_on_cau = current_track > destination_track
                elif cau_1_track > cau_2_track:
                    change_track_on_cau = current_track < destination_track

        def check_last_space(space: str):
            return space == self.destination or (
                self.destination in BACKEND_GAME_DATA.bds_group["R"].bds
                and space == self.destination + "A"
            )

        new_space = calc_new_space(
            game_state=game_state,
            current_space=current_space_id,
            FRONTEND_GAME_DATA=FRONTEND_GAME_DATA,
            BACKEND_GAME_DATA=BACKEND_GAME_DATA,
            check_last_space=check_last_space,
            change_track_on_cau=change_track_on_cau,
            change_track_on_r=change_track_on_r,
            draw_movement_lines=True,
        )

        game_state.logic.player[self.player].at = new_space
        new_board = FRONTEND_GAME_DATA.space[new_space].board
        game_state.effect.board = new_board

        cw = CaseWrapper(
            FRONTEND_GAME_DATA=FRONTEND_GAME_DATA,
            game_state=game_state,
            new_space=new_space,
            player=self.player,
        )

        for c in CASE_PASS:
            game_state, task, out = c(cw)
            if out:
                return game_state, task

        if not check_last_space(new_space):
            task = MoveToSpaceTask(
                destination=self.destination,
                player=self.player,
            )
            game_state.effect.wait_ms = 100
            return game_state, task

        task = LandTask(
            new_space=new_space,
            player=self.player,
            steps=game_state.logic.steps,
        )
        game_state.effect.wait_ms = 200
        return game_state, task
