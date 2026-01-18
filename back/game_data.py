import json
import os
from game_model import Card, BDS

current_dir = os.path.dirname(os.path.abspath(__file__))  # /back


def load_json(file_path):
    full_path = os.path.join(current_dir, file_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


TRACK_DATA = load_json("data/track.json")
KV_DATA = [Card(**card) for card in load_json("data/kv.json")]
CH_DATA = [Card(**card) for card in load_json("data/ch.json")]
BDS_DATA = [BDS(**property) for property in load_json("data/bds.json")]
