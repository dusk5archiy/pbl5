from game_model import PendingAction, GameState
from pydantic import BaseModel
from game_logic import (
    update_all_bds_actions,
)

# -----------------------------------------------------------------------------


class NextTurnRequest(BaseModel):
    game_state: GameState


class NextTurnResponse(BaseModel):
    new_game_state: GameState


# -----------------------------------------------------------------------------


def next_turn(request: NextTurnRequest):
    game_state = request.game_state

    # Find the end_turn action to determine if we should switch players
    end_turn_action = next(
        (action for action in game_state.pending_actions if action.type == "end_turn"),
        None,
    )

    should_switch_player = True
    if end_turn_action:
        should_switch_player = end_turn_action.data.get("next_player", True)

    # Clear all pending actions when turn ends
    game_state.pending_actions = []

    if should_switch_player:
        # Switch to next player
        player_queue = game_state.player_queue
        current_player = game_state.current_player
        current_index = player_queue.index(current_player)
        next_index = (current_index + 1) % len(player_queue)
        game_state.current_player = player_queue[next_index]
        game_state.double_roll_stack = 0  # Reset for new player
    # else: keep current player (doubles case)

    # Update all BDS action flags for the current player
    update_all_bds_actions(game_state, game_state.current_player)

    # Add roll_dice action for the next turn
    game_state.pending_actions.append(PendingAction(type="roll_dice", data={}))

    return NextTurnResponse(new_game_state=game_state)


# -----------------------------------------------------------------------------
