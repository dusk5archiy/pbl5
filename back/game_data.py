import json
import os
from game_model import Card, BDS, Board, ColorPallete, GameData

current_dir = os.path.dirname(os.path.abspath(__file__))  # /back


def load_json(file_path):
    full_path = os.path.join(current_dir, file_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


BOARD_DATA = Board(**load_json("data/board.json"))

GAME_DATA = GameData(
    kv={key: Card(**card) for key, card in load_json("data/kv.json").items()},
    ch={key: Card(**card) for key, card in load_json("data/ch.json").items()},
    bds={key: BDS(**bds) for key, bds in load_json("data/bds.json").items()},
    vt_max=BOARD_DATA.S.__len__() + 4,
    space=BOARD_DATA.space(),
    track=BOARD_DATA.track(),
    color_pallete=ColorPallete(**load_json("data/color_pallete.json")),
    space_labels=load_json("data/space_labels.json"),
)
