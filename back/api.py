from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from game_init import init_game_state
from game_logic import move_with_dice_path
from game_model import GameState, GameData, PendingAction
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

# Space effects configuration
# Effects that trigger when touching a space (passing through or landing)
def bdau_effect(state: GameState, player_id: str) -> None:
    """Add salary when passing through or landing on BDAU"""
    state.players[player_id].budget += BDAU_SALARY


EFFECTS_ON_TOUCH: dict[str, SpaceEffect] = {
    "BDAU": bdau_effect
}

# Effects that trigger only when landing on a space
EFFECTS_ON_LAND: dict[str, SpaceEffect] = {
    # Add landing effects here
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

    # Get path
    path = move_with_dice_path(current_position, step)

    # Create intermediate game states for each step
    intermediate_states = []
    temp_state = game_state.model_copy(deep=True)  # Deep copy of initial state
    
    # Clear roll_dice action since player is now rolling
    temp_state.pending_actions = []
    
    # Update double_roll_stack based on whether doubles were rolled
    if is_doubles:
        temp_state.double_roll_stack += 1
    else:
        temp_state.double_roll_stack = 0
    
    # TODO: Handle 3 doubles jail logic later
    # For now, just let the player move normally
    
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
            # Add arrival message as pending action
            temp_state.pending_actions.append(PendingAction(
                type="show_message",
                data={
                    "message": f"Bạn đã đến ô {position}"
                }
            ))

            if position in EFFECTS_ON_LAND:
                EFFECTS_ON_LAND[position](temp_state, current_player)
            
            
            # Add end turn action with flag for next player
            if temp_state.double_roll_stack > 0 and temp_state.double_roll_stack < 3:
                # Player rolled doubles, stays with same player
                temp_state.pending_actions.append(PendingAction(
                    type="end_turn",
                    data={"next_player": False}
                ))
            else:
                # Normal turn end or 3 doubles - move to next player
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
    
    # Add roll_dice action for the next turn
    game_state.pending_actions.append(PendingAction(
        type="roll_dice",
        data={}
    ))

    return NextTurnResponse(new_game_state=game_state)


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
