from game_data import BOARD_DATA, GAME_DATA
from game_model import GameState

BDAU_SALARY = 200


# -----------------------------------------------------------------------------
def move_with_dice_path(cur_pos: str, steps: int):
    track = BOARD_DATA.track()
    current_position = track.index(cur_pos)
    board_size = len(track)
    path = []
    for i in range(steps + 1):
        pos = (current_position + i) % board_size
        path.append(track[pos])
    return path


# -----------------------------------------------------------------------------
def calculate_player_total(state: GameState, player_id: str) -> int:
    """Calculate total wealth: budget + property values"""
    total = state.players[player_id].budget

    # Add value of all owned properties
    for property_id, property_state in state.bds.items():
        if property_state.owner == player_id:
            property_price = GAME_DATA.bds[property_id].price
            if property_state.level == -1:  # Mortgaged
                total += property_price // 2
            else:
                total += property_price

    return total


# -----------------------------------------------------------------------------
def update_all_bds_actions(state: GameState, current_player: str):
    """Update action flags for all BDS properties - only enable for current player's properties"""
    # Iterate through all properties that have been purchased
    for property_id in state.bds.keys():
        property_owner = state.bds[property_id].owner
        # Only calculate actions for properties owned by the current player
        if property_owner == current_player:
            actions = calculate_bds_actions(state, property_id, current_player)
            state.bds[property_id].can_upgrade = actions["can_upgrade"]
            state.bds[property_id].can_downgrade = actions["can_downgrade"]
            state.bds[property_id].can_mortgage = actions["can_mortgage"]
            state.bds[property_id].can_unmortgage = actions["can_unmortgage"]
        else:
            # Set all actions to False for properties not owned by current player
            state.bds[property_id].can_upgrade = False
            state.bds[property_id].can_downgrade = False
            state.bds[property_id].can_mortgage = False
            state.bds[property_id].can_unmortgage = False


# -----------------------------------------------------------------------------
def calculate_bds_actions(
    state: GameState, property_id: str, current_player: str
) -> dict:
    """
    Calculate which actions are available for a property according to monopoly rules.
    Returns dict with can_upgrade, can_downgrade, can_mortgage, can_unmortgage booleans.
    """
    property_state = state.bds.get(property_id)
    if not property_state:
        return {
            "can_upgrade": False,
            "can_downgrade": False,
            "can_mortgage": False,
            "can_unmortgage": False,
        }

    property_info = GAME_DATA.bds.get(property_id)
    if not property_info:
        return {
            "can_upgrade": False,
            "can_downgrade": False,
            "can_mortgage": False,
            "can_unmortgage": False,
        }

    # Not owned by current player - no actions available
    if property_state.owner != current_player:
        return {
            "can_upgrade": False,
            "can_downgrade": False,
            "can_mortgage": False,
            "can_unmortgage": False,
        }

    group = property_info.group
    can_upgrade = False
    can_downgrade = False
    can_mortgage = False
    can_unmortgage = False

    # Get all properties in the same group
    group_properties = GAME_DATA.group_bds.get(group, [])

    # Check if player owns all properties in the group (monopoly)
    # A monopoly exists when all properties in the group are owned by the same player
    owns_monopoly = all(
        prop_id in state.bds and state.bds[prop_id].owner == current_player
        for prop_id in group_properties
    )

    # Unmortgage: can unmortgage if property is mortgaged (-1)
    if property_state.level == -1:
        unmortgage_price = property_info.unmortgage
        can_unmortgage = state.players[current_player].budget >= unmortgage_price

    # Mortgage: can mortgage if property is level 0 and no other property in group has houses
    if property_state.level == 0:
        # Check that no other property in the group has houses (level > 0)
        no_houses_in_group = all(
            state.bds[prop_id].level <= 0
            for prop_id in group_properties
            if prop_id in state.bds and state.bds[prop_id].owner == current_player
        )
        can_mortgage = no_houses_in_group

    # Upgrade: can upgrade if owns monopoly, property not mortgaged, has upgrade option, and even building rule
    if (
        owns_monopoly
        and property_state.level >= 0
        and property_info.upgrade is not None
    ):
        # Check even building rule: can't upgrade if this would make level more than 1 higher than others
        # Since we have a monopoly, all properties in the group are owned by current_player and in state.bds
        # Find minimum level among OTHER properties in the group (excluding current property)
        other_properties_levels = [
            state.bds[prop_id].level
            for prop_id in group_properties
            if prop_id != property_id
        ]

        # Can upgrade if: no other properties OR new level won't exceed others by more than 1
        if not other_properties_levels or property_state.level <= min(
            other_properties_levels
        ):
            max_level = len(property_info.rent) - 1  # Maximum level is last rent index
            if property_state.level < max_level:
                upgrade_price = property_info.upgrade
                # Check budget and building supply
                has_budget = state.players[current_player].budget >= upgrade_price
                # Level 0-3 requires houses, level 4 (hotel) requires a hotel
                if (
                    property_state.level < max_level - 1
                ):  # Building houses (levels 0->1, 1->2, 2->3, 3->4 for most)
                    has_supply = state.houses_left > 0
                else:  # Building hotel (last upgrade)
                    has_supply = state.hotels_left > 0
                can_upgrade = has_budget and has_supply

    # Downgrade: can downgrade if property level > 0 and not mortgaged, and even building rule
    if property_state.level > 0:
        # Check even building rule: can't downgrade if this would make level more than 1 lower than others
        # Get max level among all properties in the group owned by this player
        max_level = max(
            state.bds[prop_id].level
            for prop_id in group_properties
            if prop_id in state.bds and state.bds[prop_id].owner == current_player
        )
        if (
            property_state.level >= max_level
        ):  # Can downgrade if at or above maximum level
            can_downgrade = True

    return {
        "can_upgrade": can_upgrade,
        "can_downgrade": can_downgrade,
        "can_mortgage": can_mortgage,
        "can_unmortgage": can_unmortgage,
    }
