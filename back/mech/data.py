from game_model import GameData
from game_data import GAME_DATA
from pydantic import BaseModel

# -----------------------------------------------------------------------------


class GameDataResponse(BaseModel):
    game_data: GameData


def get_game_data():
    return GameDataResponse(game_data=GAME_DATA)


# -----------------------------------------------------------------------------
