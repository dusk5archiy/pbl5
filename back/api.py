from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from game_init import init_game_state
from board_utils import get_steps_path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global game state
game_state = None

class PlayerOrder(BaseModel):
    players: List[str]  # e.g., ["red", "green", "blue"]

class DiceRoll(BaseModel):
    dice1: int
    dice2: int

@app.post("/init_game")
async def init_game(player_order: PlayerOrder):
    global game_state
    game_state = init_game_state(player_order.players)
    return game_state

@app.post("/roll_dice")
async def roll_dice(dice_roll: DiceRoll):
    global game_state
    if game_state is None:
        return {"error": "Game not initialized. Call /init_game first."}

    step = dice_roll.dice1 + dice_roll.dice2
    current_player = game_state["current_player"]
    current_position = game_state["players"][current_player]["at"]

    # Get path
    path = get_steps_path(current_position, step)

    # Update position
    new_position = path[-1]  # Last element in path
    game_state["players"][current_player]["at"] = new_position

    # TODO: Handle special tiles, money changes, etc.
    # For now, just update position

    # Switch to next player (simple round-robin)
    player_queue = game_state["player_queue"]
    current_index = player_queue.index(current_player)
    next_index = (current_index + 1) % len(player_queue)
    game_state["current_player"] = player_queue[next_index]

    return {
        "path": path,
        "new_position": new_position,
        "current_player": current_player,
        "next_player": game_state["current_player"]
    }

@app.get("/game_state")
async def get_game_state():
    return game_state

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)