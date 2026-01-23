import json
import os
from game_model import Card, BDS, Board, ColorPallete, GameData

current_dir = os.path.dirname(os.path.abspath(__file__))  # /back


def load_json(file_path):
    full_path = os.path.join(current_dir, file_path)
    with open(full_path, "r", encoding="utf-8") as f:
        return json.load(f)


BOARD_DATA = Board(**load_json("data/board.json"))

# Build group_bds mapping
bds_data = load_json("data/bds.json")
group_bds = {}
for bds_id, bds_info in bds_data.items():
    group = bds_info["group"]
    if group not in group_bds:
        group_bds[group] = []
    group_bds[group].append(bds_id)
    
    # Calculate unmortgage (110% of mortgage)
    bds_info["unmortgage"] = int(bds_info["mortgage"] * 1.1)
    
    # Calculate downgrade (50% of upgrade if upgrade exists)
    if "upgrade" in bds_info and bds_info["upgrade"] is not None:
        bds_info["downgrade"] = bds_info["upgrade"] // 2
    else:
        bds_info["downgrade"] = None

# Sort property IDs within each group
for group in group_bds:
    group_bds[group].sort()

GAME_DATA = GameData(
    kv={key: Card(**card) for key, card in load_json("data/kv.json").items()},
    ch={key: Card(**card) for key, card in load_json("data/ch.json").items()},
    bds={key: BDS(**bds) for key, bds in bds_data.items()},
    vt_max=BOARD_DATA.S.__len__() + 4,
    space=BOARD_DATA.space(),
    track=BOARD_DATA.track(),
    color_pallete=ColorPallete(**load_json("data/color_pallete.json")),
    space_labels=load_json("data/space_labels.json"),
    special_spaces=BOARD_DATA.special_spaces(),
    bds_groups_order=BOARD_DATA.bds_groups_order,
    group_bds=group_bds,
)
