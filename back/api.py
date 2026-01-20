from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from game_init import init_game_state
from game_logic import move_with_dice_path
from game_model import GameState, GameData
from pydantic import BaseModel
from game_data import GAME_DATA

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------


class PlayerOrder(BaseModel):
    players: list[str]


class InitGameResponse(BaseModel):
    game_state: GameState


@app.post("/init_game", response_model=InitGameResponse)
async def init_game(player_order: PlayerOrder):
    game_state = init_game_state(player_order.players)
    return InitGameResponse(game_state=game_state)


# -----------------------------------------------------------------------------


class RollDiceResponse(BaseModel):
    new_game_state: GameState
    path: list[str]


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

    # Get current position
    current_player = game_state.current_player
    current_position = game_state.players[current_player].at

    # Get path
    path = move_with_dice_path(current_position, step)

    # Update position:
    new_position = path[-1]
    game_state.players[current_player].at = new_position

    return RollDiceResponse(
        new_game_state=game_state,
        path=path,
    )


# -----------------------------------------------------------------------------


class NextPlayerRequest(BaseModel):
    game_state: GameState


class NextPlayerResponse(BaseModel):
    new_game_state: GameState


@app.post("/next_player", response_model=NextPlayerResponse)
async def next_player(request: NextPlayerRequest):
    game_state = request.game_state

    # Switch to next player (simple round-robin)
    player_queue = game_state.player_queue
    current_player = game_state.current_player
    current_index = player_queue.index(current_player)
    next_index = (current_index + 1) % len(player_queue)
    game_state.current_player = player_queue[next_index]

    return NextPlayerResponse(new_game_state=game_state)


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
