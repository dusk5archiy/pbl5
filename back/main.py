from board_utils import get_steps_path
from game_init import init_game_state

if __name__ == "__main__":
    result = get_steps_path("TT", 12)
    print(result)

    player_order = ["red", "green", "blue"]
    game_state = init_game_state(player_order)
    print("Game initialized for players:", player_order)
    print(game_state)