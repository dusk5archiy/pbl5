import random
from game_data import GAME_DATA
from game_model import GameState, GameStatePlayer


def init_game_state(player_order: list[str]):
    kv_queue = list(GAME_DATA.kv.keys())
    ch_queue = list(GAME_DATA.ch.keys())

    random.shuffle(kv_queue)
    random.shuffle(ch_queue)

    players = {}
    for color in player_order:
        players[color] = GameStatePlayer(budget=1500, at="BDAU")

    game_state = GameState(
        kv_queue=kv_queue,
        ch_queue=ch_queue,
        bds={},
        cards={},
        player_queue=player_order,
        players=players,
        current_player=player_order[0] if player_order else "",
        double_roll_stack=0,
        pending_actions=[],
    )

    return game_state
