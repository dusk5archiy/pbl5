from game_init import init_game_state
from pydantic import BaseModel
from game_model import PendingAction, GameState
from game_logic import (
    update_all_bds_actions,
)

# -----------------------------------------------------------------------------


class InitGameRequest(BaseModel):
    players: list[str]


class InitGameResponse(BaseModel):
    game_state: GameState


# -----------------------------------------------------------------------------


def init_game(player_order: InitGameRequest):
    game_state = init_game_state(player_order.players)

    # Add roll_dice action at the start of the game
    game_state.pending_actions.append(PendingAction(type="roll_dice", data={}))

    # Initialize property action flags
    update_all_bds_actions(game_state, game_state.current_player)

    return InitGameResponse(game_state=game_state)


# -----------------------------------------------------------------------------
