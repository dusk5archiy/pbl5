from pydantic import BaseModel
from game_model import PendingAction, GameState
from game_data import GAME_DATA
from game_logic import (
    calculate_player_total,
    update_all_bds_actions,
)

# -----------------------------------------------------------------------------


class BuyPropertyRequest(BaseModel):
    game_state: GameState
    property_id: str
    buy: bool


class BuyPropertyResponse(BaseModel):
    new_game_state: GameState


# -----------------------------------------------------------------------------


def buy_property(request: BuyPropertyRequest):
    game_state = request.game_state.model_copy(deep=True)
    property_id = request.property_id
    buy = request.buy
    current_player = game_state.current_player

    # Remove the buy_property pending action
    game_state.pending_actions = [
        action
        for action in game_state.pending_actions
        if not (
            action.type == "buy_property"
            and action.data.get("property_id") == property_id
        )
    ]

    if buy:
        # Check if property exists and player has enough money
        if property_id in GAME_DATA.bds:
            property_price = GAME_DATA.bds[property_id].price
            player_budget = game_state.players[current_player].budget

            if player_budget >= property_price:
                # Deduct money
                game_state.players[current_player].budget -= property_price

                # Assign ownership
                from game_model import GameStateBDS

                game_state.bds[property_id] = GameStateBDS(
                    owner=current_player, level=0
                )

                # Recalculate total wealth (budget + property values)
                game_state.players[current_player].total = calculate_player_total(
                    game_state, current_player
                )

                # Update all BDS action flags
                update_all_bds_actions(game_state, current_player)

                # Add success message
                game_state.pending_actions.append(
                    PendingAction(
                        type="show_message",
                        data={
                            "message": f"Đã mua {property_id} với giá {property_price}k"
                        },
                    )
                )

    return BuyPropertyResponse(new_game_state=game_state)


# -----------------------------------------------------------------------------


class PayRentRequest(BaseModel):
    game_state: GameState
    property_id: str


class PayRentResponse(BaseModel):
    new_game_state: GameState


# -----------------------------------------------------------------------------


def pay_rent(request: PayRentRequest):
    game_state = request.game_state.model_copy(deep=True)
    property_id = request.property_id
    current_player = game_state.current_player

    # Remove the pay_rent pending action
    game_state.pending_actions = [
        action
        for action in game_state.pending_actions
        if not (
            action.type == "pay_rent" and action.data.get("property_id") == property_id
        )
    ]

    # Get property state and calculate rent
    property_state = game_state.bds.get(property_id)
    property_info = GAME_DATA.bds.get(property_id)

    if (
        property_state
        and property_info
        and property_state.owner != current_player
        and property_state.level >= 0
    ):
        rent_level = min(property_state.level, len(property_info.rent) - 1)
        rent_amount = property_info.rent[rent_level]

        # Transfer rent from current player to owner
        game_state.players[current_player].budget -= rent_amount
        game_state.players[property_state.owner].budget += rent_amount

        # Update totals
        game_state.players[current_player].total = calculate_player_total(
            game_state, current_player
        )
        game_state.players[property_state.owner].total = calculate_player_total(
            game_state, property_state.owner
        )

        # Add message
        game_state.pending_actions.append(
            PendingAction(
                type="show_message",
                data={
                    "message": f"Đã trả thuê {rent_amount}k cho {property_state.owner}"
                },
            )
        )

    return PayRentResponse(new_game_state=game_state)


# -----------------------------------------------------------------------------
