from game_model import PendingAction, GameState
from pydantic import BaseModel
from game_logic import (
    calculate_player_total,
)

# -----------------------------------------------------------------------------


class PayTaxRequest(BaseModel):
    game_state: GameState


class PayTaxResponse(BaseModel):
    new_game_state: GameState


# -----------------------------------------------------------------------------


def pay_tax(request: PayTaxRequest):
    game_state = request.game_state.model_copy(deep=True)
    current_player = game_state.current_player

    # Find and process pay_tax action
    tax_action = next(
        (action for action in game_state.pending_actions if action.type == "pay_tax"),
        None,
    )

    if tax_action:
        tax_type = tax_action.data.get("tax_type")
        tax_amount = tax_action.data.get("amount")

        # Deduct tax
        if tax_amount:
            game_state.players[current_player].budget -= tax_amount
        game_state.players[current_player].total = calculate_player_total(
            game_state, current_player
        )

        # Remove pay_tax action
        game_state.pending_actions = [
            action for action in game_state.pending_actions if action.type != "pay_tax"
        ]

        # Add message
        tax_name = "Thuế thu nhập" if tax_type == "income" else "Thuế xa xỉ"
        game_state.pending_actions.append(
            PendingAction(
                type="show_message", data={"message": f"{tax_name}: -{tax_amount}k"}
            )
        )

    return PayTaxResponse(new_game_state=game_state)


# -----------------------------------------------------------------------------
