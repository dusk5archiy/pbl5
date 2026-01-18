import json
import os
import random
from json_loader import KV_DATA, CH_DATA

def get_shuffled_queue(cards):
    """Shuffle the list of card IDs"""
    ids = [card['id'] for card in cards]
    random.shuffle(ids)
    return ids

def init_game_state(player_order):
    """
    Khởi tạo trạng thái game ban đầu.
    player_order: list thứ tự người chơi, ví dụ ["red", "green", "blue"]
    Trả về: dict trạng thái game
    """
    # Load và shuffle queues
    kv_queue = get_shuffled_queue(KV_DATA)
    ch_queue = get_shuffled_queue(CH_DATA)

    # Tạo players dict
    players = {}
    for color in player_order:
        players[color] = {
            "budget": 1500,
            "at": "BDAU"
        }

    # Trạng thái game
    game_state = {
        "kv_queue": kv_queue,
        "ch_queue": ch_queue,
        "bds": {},
        "cards": {},
        "player_queue": player_order,
        "players": players,
        "current_player": player_order[0] if player_order else None,
        "double_roll_stack": 0
    }

    return game_state
