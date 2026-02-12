from model.game_state import GameState, Task, TaskResult
from game_data_manager import GAME_DATA
from calc.mod import mod_intermediate, mod_move

from task.move import MoveNearestTask, MoveToSpaceTask
from calc.switch import change_track_on_cau_condition, change_track_on_r_condition


# -----------------------------------------------------------------------------


class DiceCTask(Task):
    def __call__(self, game_state: GameState) -> TaskResult:
        assert game_state.current_chore.dice_c is not None
        game_data = GAME_DATA[game_state.version]
        BACKEND_GAME_DATA = game_data.backend_game_data
        game_state.chore.dice_c.pop(0)

        original_space = game_state.logic.player[game_state.logic.current_player].at
        exists_unowned = any(
            game_state.logic.bds[bds].owner is None for bds in game_state.logic.bds
        )

        game_state.effect.movement_lines.clear()
        game_state = mod_move(game_state)
        player = game_state.logic.current_player

        def criteria(game_state: GameState, bds: str):
            if exists_unowned:
                return game_state.logic.bds[bds].owner is None
            return (
                game_state.logic.bds[bds].owner != player
                and game_state.logic.bds[bds].level != -1
            )

        def check_last_space(space: str):
            for s in BACKEND_GAME_DATA.bds_group["R"].bds:
                if space == s + "A":
                    return criteria(game_state, s)

            if space not in game_state.logic.bds:
                return False

            return criteria(game_state, space)

        assert (steps := game_state.logic.steps) is not None
        task = MoveNearestTask.create(
            original_space=original_space,
            steps=steps,
            player=game_state.logic.current_player,
            check_last_space=check_last_space,
        )
        game_state = mod_intermediate(game_state)
        return game_state, task


# -----------------------------------------------------------------------------


class DiceXbTask(Task):
    def __call__(self, game_state: GameState) -> TaskResult:
        assert game_state.current_chore.dice_xb is not None
        game_state.chore.dice_xb.pop(0)
        game_data = GAME_DATA[game_state.version]
        FRONTEND_GAME_DATA = game_data.frontend_game_data

        original_space = game_state.logic.player[game_state.logic.current_player].at

        def check_last_space(space: str):
            return space in FRONTEND_GAME_DATA.action

        game_state = MoveNearestTask.prepare(game_state)
        assert (steps := game_state.logic.steps) is not None
        task = MoveNearestTask(
            original_space=original_space,
            change_track_on_cau=change_track_on_cau_condition(steps),
            change_track_on_r=change_track_on_r_condition(steps),
            player=game_state.logic.current_player,
            check_last_space=check_last_space,
        )
        game_state = mod_intermediate(game_state)
        return game_state, task


# -----------------------------------------------------------------------------


class TripleDiceTask(Task):
    destination: str

    def __call__(self, game_state: GameState) -> TaskResult:
        assert (chore := game_state.current_chore.triple_dice) is not None
        game_state.chore.triple_dice.remove(chore)
        game_state = MoveToSpaceTask.prepare(game_state)
        task = MoveToSpaceTask(
            destination=self.destination,
            player=game_state.logic.current_player,
        )
        game_state = mod_intermediate(game_state)
        return game_state, task


# -----------------------------------------------------------------------------
