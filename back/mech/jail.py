from game_model import PendingAction, GameState
from pydantic import BaseModel
from game_logic import (
    calculate_player_total,
)

# -----------------------------------------------------------------------------


class PayJailFineRequest(BaseModel):
    game_state: GameState
    dice1: int | None = None
    dice2: int | None = None


class PayJailFineResponse(BaseModel):
    new_game_state: GameState
    should_move: bool = False
    dice1: int | None = None
    dice2: int | None = None


# -----------------------------------------------------------------------------


def pay_jail_fine(request: PayJailFineRequest):
    game_state = request.game_state.model_copy(deep=True)
    current_player = game_state.current_player

    # Check if player is in jail
    if game_state.players[current_player].in_jail:
        # Pay 50k to exit jail
        game_state.players[current_player].budget -= 50
        game_state.players[current_player].in_jail = False
        game_state.players[current_player].jail_turns = 0
        game_state.players[current_player].total = calculate_player_total(
            game_state, current_player
        )
        # Move player to TT (just visiting)
        game_state.players[current_player].at = "TT"

        # If dice values provided (forced payment), player should move
        if request.dice1 is not None and request.dice2 is not None:
            # Clear all pending actions - movement will create new ones
            game_state.pending_actions = []

            return PayJailFineResponse(
                new_game_state=game_state,
                should_move=True,
                dice1=request.dice1,
                dice2=request.dice2,
            )
        else:
            # Voluntary payment - just remove forced action and add message
            game_state.pending_actions = [
                action
                for action in game_state.pending_actions
                if action.type != "pay_jail_fine_forced"
            ]

            game_state.pending_actions.append(
                PendingAction(
                    type="show_message", data={"message": "Đã trả 50k để ra tù"}
                )
            )

    return PayJailFineResponse(new_game_state=game_state)


# -----------------------------------------------------------------------------
