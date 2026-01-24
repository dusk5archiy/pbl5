from game_logic import move_with_dice_path
from pydantic import BaseModel
from game_model import PendingAction, GameStateBDS, GameState
from game_data import GAME_DATA
from game_logic import (
    BDAU_SALARY,
)
from game_effect import EFFECTS_ON_TOUCH, EFFECTS_ON_LAND, go_to_jail_effect

# -----------------------------------------------------------------------------


class RollDiceRequest(BaseModel):
    game_state: GameState
    dice1: int
    dice2: int


class RollDiceResponse(BaseModel):
    intermediate_states: list[GameState]

    # -----------------------------------------------------------------------------


def move_with_dice(request: RollDiceRequest):
    game_state = request.game_state

    # Calculate steps to move
    dice1 = request.dice1
    dice2 = request.dice2
    step = dice1 + dice2
    is_doubles = dice1 == dice2

    # Get current position
    current_player = game_state.current_player
    current_position = game_state.players[current_player].at

    # Create intermediate game states
    intermediate_states = []
    temp_state = game_state.model_copy(deep=True)

    # Clear roll_dice action since player is now rolling
    temp_state.pending_actions = []

    # Handle jail logic
    if temp_state.players[current_player].in_jail:
        if is_doubles:
            # Rolled doubles - exit jail and move
            temp_state.players[current_player].in_jail = False
            temp_state.players[current_player].jail_turns = 0
            temp_state.double_roll_stack = 0  # No double bonus when exiting jail
            # Move player to TT (just visiting) before moving with dice
            temp_state.players[current_player].at = "TT"
            current_position = "TT"  # Update current position for path calculation

            temp_state.pending_actions.append(
                PendingAction(
                    type="show_message", data={"message": "Ra tù với số đôi."}
                )
            )
        else:
            # Did not roll doubles
            temp_state.players[current_player].jail_turns += 1

            if temp_state.players[current_player].jail_turns >= 3:
                # Third turn - must pay to exit (show popup for confirmation)
                temp_state.double_roll_stack = 0

                temp_state.pending_actions.append(
                    PendingAction(
                        type="pay_jail_fine_forced",
                        data={"forced": True, "dice1": dice1, "dice2": dice2},
                    )
                )
                temp_state.pending_actions.append(
                    PendingAction(type="end_turn", data={"next_player": True})
                )
                intermediate_states.append(temp_state.model_copy(deep=True))
                return RollDiceResponse(intermediate_states=intermediate_states)
            else:
                # Still in jail
                temp_state.double_roll_stack = 0
                temp_state.pending_actions.append(
                    PendingAction(
                        type="show_message",
                        data={
                            "message": f"Vẫn ở tù (lượt {temp_state.players[current_player].jail_turns}/3)"
                        },
                    )
                )

                # Add end_turn action and return early - player doesn't move
                temp_state.pending_actions.append(
                    PendingAction(type="end_turn", data={"next_player": True})
                )
                intermediate_states.append(temp_state)
                return RollDiceResponse(intermediate_states=intermediate_states)
    else:
        # Not in jail - normal roll logic
        if is_doubles:
            temp_state.double_roll_stack += 1
            if temp_state.double_roll_stack >= 3:
                # Three doubles in a row - go to jail
                temp_state.players[current_player].in_jail = True
                temp_state.players[current_player].jail_turns = 0
                temp_state.double_roll_stack = 0

                temp_state.pending_actions.append(
                    PendingAction(
                        type="show_message",
                        data={"message": "Ba lần số đôi liên tiếp - vào tù!"},
                    )
                )
                # Add state with player at current position
                intermediate_states.append(temp_state.model_copy(deep=True))

                # Now jump to OT (no path drawn)
                temp_state.players[current_player].at = "OT"
                temp_state.pending_actions = []
                temp_state.pending_actions.append(
                    PendingAction(type="end_turn", data={"next_player": True})
                )
                intermediate_states.append(temp_state.model_copy(deep=True))
                return RollDiceResponse(intermediate_states=intermediate_states)
        else:
            temp_state.double_roll_stack = 0

    # Get path and move player
    path = move_with_dice_path(current_position, step)

    for i, position in enumerate(path):
        temp_state.players[current_player].at = position

        # Apply on-touch effects (skip starting position)
        if i > 0 and position in EFFECTS_ON_TOUCH:
            EFFECTS_ON_TOUCH[position](temp_state, current_player)

            # Add message for passing through BDAU
            if position == "BDAU":
                temp_state.pending_actions.append(
                    PendingAction(
                        type="show_message",
                        data={"message": f"Qua ô Bắt đầu (+{BDAU_SALARY}k)"},
                    )
                )

        # Apply on-land effects (only on final position)
        if i == len(path) - 1:
            # Check for go to jail first
            if position == "VT":
                go_to_jail_effect(temp_state, current_player)
                temp_state.pending_actions.append(
                    PendingAction(type="show_message", data={"message": "Vào tù!"})
                )
                # Add state with player at VT
                intermediate_states.append(temp_state.model_copy(deep=True))

                # Now jump to OT (no path drawn)
                temp_state.players[current_player].at = "OT"
                temp_state.pending_actions = []
                temp_state.pending_actions.append(
                    PendingAction(type="end_turn", data={"next_player": True})
                )
                intermediate_states.append(temp_state.model_copy(deep=True))
                return RollDiceResponse(intermediate_states=intermediate_states)

            # Add arrival message as pending action
            temp_state.pending_actions.append(
                PendingAction(
                    type="show_message", data={"message": f"Bạn đã đến ô {position}"}
                )
            )

            if position in EFFECTS_ON_LAND:
                EFFECTS_ON_LAND[position](temp_state, current_player)

            # Check if this is an unowned property
            if position in GAME_DATA.bds:
                property_state = temp_state.bds.get(position)
                if not property_state or property_state.owner == "":
                    # Property is unowned, check if player can buy
                    property_price = GAME_DATA.bds[position].price
                    player_budget = temp_state.players[current_player].budget
                    buyable = player_budget >= property_price

                    temp_state.pending_actions.append(
                        PendingAction(
                            type="buy_property",
                            data={
                                "property_id": position,
                                "price": property_price,
                                "buyable": buyable,
                            },
                        )
                    )
                elif (
                    property_state.owner != current_player and property_state.level >= 0
                ):
                    # Property is owned by another player and not mortgaged, pay rent
                    property_info = GAME_DATA.bds[position]

                    # Calculate rent based on property type
                    if property_info.group == "R":
                        # Railroad: rent based on number of railroads owned
                        # 1 railroad -> rent[0]=25k, 2 -> rent[1]=50k, 3 -> rent[2]=100k, 4 -> rent[3]=200k
                        railroads_owned = sum(
                            1
                            for prop_id in GAME_DATA.group_bds["R"]
                            if temp_state.bds.get(
                                prop_id, GameStateBDS(owner="", level=-1)
                            ).owner
                            == property_state.owner
                            and temp_state.bds.get(
                                prop_id, GameStateBDS(owner="", level=-1)
                            ).level
                            >= 0
                        )
                        rent_level = max(
                            0, min(railroads_owned - 1, len(property_info.rent) - 1)
                        )
                        rent_amount = property_info.rent[rent_level]
                    elif property_info.group == "U":
                        # Utility: base rent (4k or 10k) multiplied by dice score
                        # 1 utility -> 4k * dice, 2 utilities -> 10k * dice
                        utilities_owned = sum(
                            1
                            for prop_id in GAME_DATA.group_bds["U"]
                            if temp_state.bds.get(
                                prop_id, GameStateBDS(owner="", level=-1)
                            ).owner
                            == property_state.owner
                            and temp_state.bds.get(
                                prop_id, GameStateBDS(owner="", level=-1)
                            ).level
                            >= 0
                        )
                        base_rent_index = max(
                            0, min(utilities_owned - 1, len(property_info.rent) - 1)
                        )
                        base_rent = property_info.rent[base_rent_index]  # 4 or 10
                        rent_amount = base_rent * step  # base * dice_sum
                    else:
                        # Regular property: use level for rent
                        rent_level = min(
                            property_state.level, len(property_info.rent) - 1
                        )
                        rent_amount = property_info.rent[rent_level]

                    temp_state.pending_actions.append(
                        PendingAction(
                            type="pay_rent",
                            data={
                                "property_id": position,
                                "owner": property_state.owner,
                                "rent": rent_amount,
                            },
                        )
                    )

            # Add end turn action with flag for next player
            # If exited jail with doubles, don't give another turn
            if temp_state.double_roll_stack > 0 and temp_state.double_roll_stack < 3:
                # Player rolled doubles and didn't exit jail - stays with same player
                temp_state.pending_actions.append(
                    PendingAction(type="end_turn", data={"next_player": False})
                )
            else:
                # Normal turn end, exited jail, or 3 doubles - move to next player
                temp_state.pending_actions.append(
                    PendingAction(type="end_turn", data={"next_player": True})
                )

        intermediate_states.append(temp_state.model_copy(deep=True))

    return RollDiceResponse(
        intermediate_states=intermediate_states,
    )


# -----------------------------------------------------------------------------
