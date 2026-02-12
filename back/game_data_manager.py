import json

from pydantic import BaseModel

from model.bds import BDSDataModel
from model.board import (
    ActionSystemModel,
    GameDataTrackModel,
    GameDataBoardModel,
    GameDataBoardSystemModel,
)
from model.game_data import BackendLogic, FrontendGameData, BackendGameData, ActionCard

from utl.format import format_budget

# -----------------------------------------------------------------------------


class GameData(BaseModel):
    frontend_game_data: FrontendGameData
    backend_game_data: BackendGameData


def fetch_game_data(version: str = "1"):
    with open(f"data/game{version}.json", encoding="utf-8") as f:
        game_json = json.load(f)
    board_validated = GameDataBoardSystemModel(
        boards=[
            GameDataBoardModel(
                tracks=[GameDataTrackModel(**track) for track in board],
            )
            for board in game_json["board"]
        ]
    )

    bds_data_validated = BDSDataModel(**game_json["bds"])
    action_validated = ActionSystemModel(**game_json["action"])

    game_data_space = board_validated.space()
    special_space = board_validated.special_space()
    space_id_list = board_validated.space_id_list()
    board_size = board_validated.size()
    track_border = board_validated.track_border()

    # -----

    path = board_validated.path()
    # -----

    game_data_bds, game_data_bds_group = bds_data_validated.export()
    game_data_bds_selector: list[list[dict[str, list[str]]]] = [
        [{} for _ in range(board.num_tracks)] for board in board_validated.boards
    ]

    for bds_id in game_data_bds.keys():
        space = game_data_space[bds_id]
        bds = game_data_bds[bds_id]
        board = space.board
        track = space.track
        group = bds.group

        if group not in game_data_bds_selector[board][track]:
            game_data_bds_selector[board][track][group] = [bds_id]
        else:
            game_data_bds_selector[board][track][group].append(bds_id)

    # -----

    backend_action_cards = action_validated.export_action_cards()
    backend_logic = BackendLogic(**game_json["logic"])
    constants = backend_logic.constants

    game_data_action_card = {group: {} for group in backend_action_cards}
    for group in backend_action_cards:
        for card_id in backend_action_cards[group]:
            info = backend_action_cards[group][card_id]
            values = info.values

            if values is not None:
                constants = values | constants

            if info.move is not None:
                vals = {}
                if info.move in game_data_bds:
                    vals["id"] = info.move
                    vals["name"] = game_data_bds[info.move].name
                elif info.move in action_validated.label:
                    vals["name"] = action_validated.label[info.move]
                constants = constants | vals

            if info.collect is not None:
                vals = {"$amount": info.collect}
                constants = constants | vals

            if info.pay is not None:
                vals = {"$amount": info.pay}
                constants = constants | vals

            vals_for_name = {
                key: format_budget(value) if key.startswith("$") else value
                for key, value in constants.items()
            }

            name = info.name.format(**vals_for_name)
            content = info.content.format(**vals_for_name)
            foot = info.foot

            game_data_action_card[group][card_id] = ActionCard(
                name=name,
                content=content,
                foot=foot,
            )

    frontend_game_data = FrontendGameData(
        space=game_data_space,
        space_id_list=space_id_list,
        board_size=board_size,
        pallete=game_json["pallete"],
        bds=game_data_bds,
        special_space=special_space,
        track_border=track_border,
        action=action_validated.export_action_space(),
        action_label=action_validated.label,
        action_special_label=action_validated.special_label,
        bds_selector=game_data_bds_selector,
        action_card=game_data_action_card,
        action_name={
            group: action_validated.group[group].name
            for group in action_validated.group
        },
    )
    backend_game_data = BackendGameData(
        path=path,
        path_r={value: key for key, value in path.items()},
        bds_group=game_data_bds_group,
        logic=backend_logic,
        action_cards=backend_action_cards,
    )
    return GameData(
        frontend_game_data=frontend_game_data, backend_game_data=backend_game_data
    )


# -----------------------------------------------------------------------------

VERSIONS = ["1", "2", "5"]

GAME_DATA = {version: fetch_game_data(version) for version in VERSIONS}

# -----------------------------------------------------------------------------
