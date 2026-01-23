from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from game_init import init_game_state
from game_logic import move_with_dice_path
from game_model import GameState, GameData, PendingAction, GameStateBDS
from pydantic import BaseModel
from game_data import GAME_DATA
from typing import Callable

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------

# Type for space effect functions
SpaceEffect = Callable[[GameState, str], None]

# Game constants
BDAU_SALARY = 200

# Helper function to calculate player total wealth
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

# Space effects configuration
# Effects that trigger when touching a space (passing through or landing)
def bdau_effect(state: GameState, player_id: str) -> None:
    """Add salary when passing through or landing on BDAU"""
    state.players[player_id].budget += BDAU_SALARY
    state.players[player_id].total = calculate_player_total(state, player_id)

def go_to_jail_effect(state: GameState, player_id: str) -> None:
    """Send player to jail - mark as in jail (position updated separately)"""
    state.players[player_id].in_jail = True
    state.players[player_id].jail_turns = 0
    # Reset double roll stack when going to jail
    state.double_roll_stack = 0

EFFECTS_ON_TOUCH: dict[str, SpaceEffect] = {
    "BDAU": bdau_effect
}

# Effects that trigger only when landing on a space
EFFECTS_ON_LAND: dict[str, SpaceEffect] = {
    "VT": go_to_jail_effect  # VT is Go to Jail space
}


class PlayerOrder(BaseModel):
    players: list[str]


class InitGameResponse(BaseModel):
    game_state: GameState


@app.post("/init_game", response_model=InitGameResponse)
async def init_game(player_order: PlayerOrder):
    game_state = init_game_state(player_order.players)
    
    # Add roll_dice action at the start of the game
    game_state.pending_actions.append(PendingAction(
        type="roll_dice",
        data={}
    ))
    
    # Initialize property action flags
    update_all_bds_actions(game_state, game_state.current_player)
    
    return InitGameResponse(game_state=game_state)


# -----------------------------------------------------------------------------


class RollDiceResponse(BaseModel):
    intermediate_states: list[GameState]


class DiceRoll(BaseModel):
    dice1: int
    dice2: int


class DiceRollRequest(BaseModel):
    game_state: GameState
    dice1: int
    dice2: int


@app.post("/move_with_dice", response_model=RollDiceResponse)
async def move_with_dice(request: DiceRollRequest):
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
            
            temp_state.pending_actions.append(PendingAction(
                type="show_message",
                data={"message": "Ra tù với hòa!"}
            ))
        else:
            # Did not roll doubles
            temp_state.players[current_player].jail_turns += 1
            
            if temp_state.players[current_player].jail_turns >= 3:
                # Third turn - forced to pay
                temp_state.players[current_player].budget -= 50
                temp_state.players[current_player].in_jail = False
                temp_state.players[current_player].jail_turns = 0
                temp_state.players[current_player].total = calculate_player_total(temp_state, current_player)
                temp_state.double_roll_stack = 0
                # Move to TT before continuing movement
                temp_state.players[current_player].at = "TT"
                current_position = "TT"
                
                temp_state.pending_actions.append(PendingAction(
                    type="show_message",
                    data={"message": "Trả 50k để ra tù (bắt buộc)"}
                ))
            else:
                # Still in jail
                temp_state.double_roll_stack = 0
                temp_state.pending_actions.append(PendingAction(
                    type="show_message",
                    data={"message": f"Vẫn ở tù (lượt {temp_state.players[current_player].jail_turns}/3)"}
                ))
                
                # Add end_turn action and return early - player doesn't move
                temp_state.pending_actions.append(PendingAction(
                    type="end_turn",
                    data={"next_player": True}
                ))
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
                
                temp_state.pending_actions.append(PendingAction(
                    type="show_message",
                    data={"message": "Ba lần hòa liên tiếp - vào tù!"}
                ))
                # Add state with player at current position
                intermediate_states.append(temp_state.model_copy(deep=True))
                
                # Now jump to OT (no path drawn)
                temp_state.players[current_player].at = "OT"
                temp_state.pending_actions = []
                temp_state.pending_actions.append(PendingAction(
                    type="end_turn",
                    data={"next_player": True}
                ))
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
                temp_state.pending_actions.append(PendingAction(
                    type="show_message",
                    data={
                        "message": f"Qua ô Bắt đầu (+{BDAU_SALARY}k)"
                    }
                ))
        
        # Apply on-land effects (only on final position)
        if i == len(path) - 1:
            # Check for go to jail first
            if position == "VT":
                go_to_jail_effect(temp_state, current_player)
                temp_state.pending_actions.append(PendingAction(
                    type="show_message",
                    data={"message": "Đi xuống tù!"}
                ))
                # Add state with player at VT
                intermediate_states.append(temp_state.model_copy(deep=True))
                
                # Now jump to OT (no path drawn)
                temp_state.players[current_player].at = "OT"
                temp_state.pending_actions = []
                temp_state.pending_actions.append(PendingAction(
                    type="end_turn",
                    data={"next_player": True}
                ))
                intermediate_states.append(temp_state.model_copy(deep=True))
                return RollDiceResponse(intermediate_states=intermediate_states)
            
            # Add arrival message as pending action
            temp_state.pending_actions.append(PendingAction(
                type="show_message",
                data={
                    "message": f"Bạn đã đến ô {position}"
                }
            ))

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
                    
                    temp_state.pending_actions.append(PendingAction(
                        type="buy_property",
                        data={
                            "property_id": position,
                            "price": property_price,
                            "buyable": buyable
                        }
                    ))
                elif property_state.owner != current_player and property_state.level >= 0:
                    # Property is owned by another player and not mortgaged, pay rent
                    property_info = GAME_DATA.bds[position]
                    rent_level = min(property_state.level, len(property_info.rent) - 1)
                    rent_amount = property_info.rent[rent_level]
                    
                    temp_state.pending_actions.append(PendingAction(
                        type="pay_rent",
                        data={
                            "property_id": position,
                            "owner": property_state.owner,
                            "rent": rent_amount
                        }
                    ))
            
            # Add end turn action with flag for next player
            # If exited jail with doubles, don't give another turn
            if temp_state.double_roll_stack > 0 and temp_state.double_roll_stack < 3:
                # Player rolled doubles and didn't exit jail - stays with same player
                temp_state.pending_actions.append(PendingAction(
                    type="end_turn",
                    data={"next_player": False}
                ))
            else:
                # Normal turn end, exited jail, or 3 doubles - move to next player
                temp_state.pending_actions.append(PendingAction(
                    type="end_turn",
                    data={"next_player": True}
                ))
        
        intermediate_states.append(temp_state.model_copy(deep=True))

    return RollDiceResponse(
        intermediate_states=intermediate_states,
    )


# -----------------------------------------------------------------------------


class NextTurnRequest(BaseModel):
    game_state: GameState


class NextTurnResponse(BaseModel):
    new_game_state: GameState


@app.post("/next_turn", response_model=NextTurnResponse)
async def next_turn(request: NextTurnRequest):
    game_state = request.game_state

    # Find the end_turn action to determine if we should switch players
    end_turn_action = next(
        (action for action in game_state.pending_actions if action.type == "end_turn"),
        None
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
    game_state.pending_actions.append(PendingAction(
        type="roll_dice",
        data={}
    ))

    return NextTurnResponse(new_game_state=game_state)


# -----------------------------------------------------------------------------


def calculate_bds_actions(state: GameState, property_id: str, current_player: str) -> dict:
    """
    Calculate which actions are available for a property according to monopoly rules.
    Returns dict with can_upgrade, can_downgrade, can_mortgage, can_unmortgage booleans.
    """
    property_state = state.bds.get(property_id)
    if not property_state:
        return {"can_upgrade": False, "can_downgrade": False, "can_mortgage": False, "can_unmortgage": False}
    
    property_info = GAME_DATA.bds.get(property_id)
    if not property_info:
        return {"can_upgrade": False, "can_downgrade": False, "can_mortgage": False, "can_unmortgage": False}
    
    # Not owned by current player - no actions available
    if property_state.owner != current_player:
        return {"can_upgrade": False, "can_downgrade": False, "can_mortgage": False, "can_unmortgage": False}
    
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
    if owns_monopoly and property_state.level >= 0 and property_info.upgrade is not None:
        # Check even building rule: can't upgrade if this would make level more than 1 higher than others
        # Since we have a monopoly, all properties in the group are owned by current_player and in state.bds
        # Find minimum level among OTHER properties in the group (excluding current property)
        other_properties_levels = [
            state.bds[prop_id].level
            for prop_id in group_properties
            if prop_id != property_id
        ]
        
        # Can upgrade if: no other properties OR new level won't exceed others by more than 1
        if not other_properties_levels or property_state.level <= min(other_properties_levels):
            max_level = len(property_info.rent) - 1  # Maximum level is last rent index
            if property_state.level < max_level:
                upgrade_price = property_info.upgrade
                # Check budget and building supply
                has_budget = state.players[current_player].budget >= upgrade_price
                # Level 0-3 requires houses, level 4 (hotel) requires a hotel
                if property_state.level < max_level - 1:  # Building houses (levels 0->1, 1->2, 2->3, 3->4 for most)
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
        if property_state.level >= max_level:  # Can downgrade if at or above maximum level
            can_downgrade = True
    
    return {
        "can_upgrade": can_upgrade,
        "can_downgrade": can_downgrade,
        "can_mortgage": can_mortgage,
        "can_unmortgage": can_unmortgage
    }


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


class PropertyActionRequest(BaseModel):
    game_state: GameState
    property_id: str


class PropertyActionResponse(BaseModel):
    new_game_state: GameState


@app.post("/upgrade_property", response_model=PropertyActionResponse)
async def upgrade_property(request: PropertyActionRequest):
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
    upgrade_cost = property_info.upgrade
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
    game_state.players[current_player].total = calculate_player_total(game_state, current_player)
    update_all_bds_actions(game_state, current_player)
    
    return PropertyActionResponse(new_game_state=game_state)


@app.post("/downgrade_property", response_model=PropertyActionResponse)
async def downgrade_property(request: PropertyActionRequest):
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
    game_state.players[current_player].total = calculate_player_total(game_state, current_player)
    update_all_bds_actions(game_state, current_player)
    
    return PropertyActionResponse(new_game_state=game_state)


@app.post("/mortgage_property", response_model=PropertyActionResponse)
async def mortgage_property(request: PropertyActionRequest):
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
    game_state.players[current_player].total = calculate_player_total(game_state, current_player)
    update_all_bds_actions(game_state, current_player)
    
    return PropertyActionResponse(new_game_state=game_state)


@app.post("/unmortgage_property", response_model=PropertyActionResponse)
async def unmortgage_property(request: PropertyActionRequest):
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
    game_state.players[current_player].total = calculate_player_total(game_state, current_player)
    update_all_bds_actions(game_state, current_player)
    
    return PropertyActionResponse(new_game_state=game_state)


# -----------------------------------------------------------------------------


class BuyPropertyRequest(BaseModel):
    game_state: GameState
    property_id: str
    buy: bool


class BuyPropertyResponse(BaseModel):
    new_game_state: GameState


@app.post("/buy_property", response_model=BuyPropertyResponse)
async def buy_property(request: BuyPropertyRequest):
    game_state = request.game_state.model_copy(deep=True)
    property_id = request.property_id
    buy = request.buy
    current_player = game_state.current_player
    
    # Remove the buy_property pending action
    game_state.pending_actions = [
        action for action in game_state.pending_actions 
        if not (action.type == "buy_property" and action.data.get("property_id") == property_id)
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
                game_state.bds[property_id] = GameStateBDS(owner=current_player, level=0)
                
                # Recalculate total wealth (budget + property values)
                game_state.players[current_player].total = calculate_player_total(game_state, current_player)
                
                # Update all BDS action flags
                update_all_bds_actions(game_state, current_player)
                
                # Add success message
                game_state.pending_actions.append(PendingAction(
                    type="show_message",
                    data={
                        "message": f"Đã mua {property_id} với giá {property_price}k"
                    }
                ))
    
    return BuyPropertyResponse(new_game_state=game_state)


class PayRentRequest(BaseModel):
    game_state: GameState
    property_id: str


class PayRentResponse(BaseModel):
    new_game_state: GameState


@app.post("/pay_rent", response_model=PayRentResponse)
async def pay_rent(request: PayRentRequest):
    game_state = request.game_state.model_copy(deep=True)
    property_id = request.property_id
    current_player = game_state.current_player
    
    # Remove the pay_rent pending action
    game_state.pending_actions = [
        action for action in game_state.pending_actions 
        if not (action.type == "pay_rent" and action.data.get("property_id") == property_id)
    ]
    
    # Get property state and calculate rent
    property_state = game_state.bds.get(property_id)
    property_info = GAME_DATA.bds.get(property_id)
    
    if property_state and property_info and property_state.owner != current_player and property_state.level >= 0:
        rent_level = min(property_state.level, len(property_info.rent) - 1)
        rent_amount = property_info.rent[rent_level]
        
        # Transfer rent from current player to owner
        game_state.players[current_player].budget -= rent_amount
        game_state.players[property_state.owner].budget += rent_amount
        
        # Update totals
        game_state.players[current_player].total = calculate_player_total(game_state, current_player)
        game_state.players[property_state.owner].total = calculate_player_total(game_state, property_state.owner)
        
        # Add message
        game_state.pending_actions.append(PendingAction(
            type="show_message",
            data={
                "message": f"Đã trả thuê {rent_amount}k cho {property_state.owner}"
            }
        ))
    
    return PayRentResponse(new_game_state=game_state)


class PayJailFineRequest(BaseModel):
    game_state: GameState


class PayJailFineResponse(BaseModel):
    new_game_state: GameState


@app.post("/pay_jail_fine", response_model=PayJailFineResponse)
async def pay_jail_fine(request: PayJailFineRequest):
    game_state = request.game_state.model_copy(deep=True)
    current_player = game_state.current_player
    
    # Check if player is in jail
    if game_state.players[current_player].in_jail:
        # Pay 50k to exit jail
        game_state.players[current_player].budget -= 50
        game_state.players[current_player].in_jail = False
        game_state.players[current_player].jail_turns = 0
        game_state.players[current_player].total = calculate_player_total(game_state, current_player)
        # Move player to TT (just visiting)
        game_state.players[current_player].at = "TT"
        
        # Add message
        game_state.pending_actions.append(PendingAction(
            type="show_message",
            data={"message": "Đã trả 50k để ra tù"}
        ))
    
    return PayJailFineResponse(new_game_state=game_state)


# -----------------------------------------------------------------------------


class GameDataResponse(BaseModel):
    game_data: GameData


@app.get("/game_data", response_model=GameDataResponse)
async def get_game_data():
    return GameDataResponse(game_data=GAME_DATA)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
