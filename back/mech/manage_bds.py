from game_data import GAME_DATA
from game_model import GameState
from pydantic import BaseModel
from game_logic import (
    calculate_player_total,
    update_all_bds_actions,
    calculate_bds_actions,
)

# -----------------------------------------------------------------------------


class PropertyActionRequest(BaseModel):
    game_state: GameState
    property_id: str


class PropertyActionResponse(BaseModel):
    new_game_state: GameState


# -----------------------------------------------------------------------------


def upgrade_property(request: PropertyActionRequest):
    game_state = request.game_state.model_copy(deep=True)
    property_id = request.property_id
    current_player = game_state.current_player

    property_state = game_state.bds.get(property_id)
    property_info = GAME_DATA.bds.get(property_id)

    if not property_state or not property_info:
        return PropertyActionResponse(new_game_state=game_state)

    # Verify action is allowed
    actions = calculate_bds_actions(game_state, property_id, current_player)
    if not actions["can_upgrade"]:
        return PropertyActionResponse(new_game_state=game_state)

    # Deduct upgrade cost
    if upgrade_cost := property_info.upgrade:
        game_state.players[current_player].budget -= upgrade_cost

    # Increase level and update building supply
    old_level = game_state.bds[property_id].level
    game_state.bds[property_id].level += 1
    new_level = game_state.bds[property_id].level

    # Deduct from building supply
    max_level = len(property_info.rent) - 1
    if new_level == max_level:  # Just built a hotel
        game_state.hotels_left -= 1
        # Return 4 houses if upgrading from level 4 to hotel
        if old_level == max_level - 1:
            game_state.houses_left += 4
    else:  # Built a house
        game_state.houses_left -= 1

    # Recalculate total and update all action flags
    game_state.players[current_player].total = calculate_player_total(
        game_state, current_player
    )
    update_all_bds_actions(game_state, current_player)

    return PropertyActionResponse(new_game_state=game_state)


# -----------------------------------------------------------------------------
#
def downgrade_property(request: PropertyActionRequest):
    game_state = request.game_state.model_copy(deep=True)
    property_id = request.property_id
    current_player = game_state.current_player

    property_state = game_state.bds.get(property_id)
    property_info = GAME_DATA.bds.get(property_id)

    if not property_state or not property_info:
        return PropertyActionResponse(new_game_state=game_state)

    # Verify action is allowed
    actions = calculate_bds_actions(game_state, property_id, current_player)
    if not actions["can_downgrade"]:
        return PropertyActionResponse(new_game_state=game_state)

    # Add downgrade value to budget
    downgrade_value = property_info.downgrade if property_info.downgrade else 0
    game_state.players[current_player].budget += downgrade_value

    # Decrease level and update building supply
    old_level = game_state.bds[property_id].level
    game_state.bds[property_id].level -= 1
    new_level = game_state.bds[property_id].level

    # Return to building supply
    max_level = len(property_info.rent) - 1
    if old_level == max_level:  # Selling a hotel
        game_state.hotels_left += 1
        # Take 4 houses if downgrading from hotel to level 4
        if new_level == max_level - 1:
            game_state.houses_left -= 4
    else:  # Selling a house
        game_state.houses_left += 1

    # Recalculate total and update all action flags
    game_state.players[current_player].total = calculate_player_total(
        game_state, current_player
    )
    update_all_bds_actions(game_state, current_player)

    return PropertyActionResponse(new_game_state=game_state)


# -----------------------------------------------------------------------------


def mortgage_property(request: PropertyActionRequest):
    game_state = request.game_state.model_copy(deep=True)
    property_id = request.property_id
    current_player = game_state.current_player

    property_state = game_state.bds.get(property_id)
    property_info = GAME_DATA.bds.get(property_id)

    if not property_state or not property_info:
        return PropertyActionResponse(new_game_state=game_state)

    # Verify action is allowed
    actions = calculate_bds_actions(game_state, property_id, current_player)
    if not actions["can_mortgage"]:
        return PropertyActionResponse(new_game_state=game_state)

    # Add mortgage value to budget
    mortgage_value = property_info.mortgage
    game_state.players[current_player].budget += mortgage_value

    # Set level to -1 (mortgaged)
    game_state.bds[property_id].level = -1

    # Recalculate total and update all action flags
    game_state.players[current_player].total = calculate_player_total(
        game_state, current_player
    )
    update_all_bds_actions(game_state, current_player)

    return PropertyActionResponse(new_game_state=game_state)


# -----------------------------------------------------------------------------


def unmortgage_property(request: PropertyActionRequest):
    game_state = request.game_state.model_copy(deep=True)
    property_id = request.property_id
    current_player = game_state.current_player

    property_state = game_state.bds.get(property_id)
    property_info = GAME_DATA.bds.get(property_id)

    if not property_state or not property_info:
        return PropertyActionResponse(new_game_state=game_state)

    # Verify action is allowed
    actions = calculate_bds_actions(game_state, property_id, current_player)
    if not actions["can_unmortgage"]:
        return PropertyActionResponse(new_game_state=game_state)

    # Deduct unmortgage cost
    unmortgage_cost = property_info.unmortgage
    game_state.players[current_player].budget -= unmortgage_cost

    # Set level to 0 (unmortgaged)
    game_state.bds[property_id].level = 0

    # Recalculate total and update all action flags
    game_state.players[current_player].total = calculate_player_total(
        game_state, current_player
    )
    update_all_bds_actions(game_state, current_player)

    return PropertyActionResponse(new_game_state=game_state)


# -----------------------------------------------------------------------------
