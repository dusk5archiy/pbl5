import random
from game_data import KV_DATA, CH_DATA
from game_model import GameState, GameStatePlayer, Card


def get_shuffled_queue(cards: list[Card]):
    ids = [card.id for card in cards]
    random.shuffle(ids)
    return ids


def init_game_state(player_order: list[str], kv=KV_DATA, ch=CH_DATA):
    kv_queue = get_shuffled_queue(kv)
    ch_queue = get_shuffled_queue(ch)

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
    )

    return game_state
