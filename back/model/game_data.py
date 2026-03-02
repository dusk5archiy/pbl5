from pydantic import BaseModel
from model.board import ActionCard, ActionCardInputModel, Space, TrackBorder, Action
from model.bds import BDS, BDSGroup


class FrontendGameData(BaseModel):
    space: dict[str, Space]
    space_id_list: list[list[str]]
    board_size: list[int]
    pallete: dict[str, str]
    bds: dict[str, BDS]
    special_space: dict[str, Space]
    track_border: list[list[TrackBorder]]
    action: dict[str, Action]
    action_label: dict[str, str]
    action_special_label: dict[str, str]
    bds_selector: list[list[dict[str, list[str]]]]
    action_card: dict[str, dict[str, ActionCard]]
    action_name: dict[str, str]
    rule: str = ""


class BackendLogic(BaseModel):
    init_budget: int
    start_at: str
    init_house: int = 0
    init_hotel: int = 0
    init_skyscraper: int = 0
    use_pool: bool = False
    use_minor_ownership: bool = False
    use_speed_dice: bool = False
    constants: dict[str, str | int]


class BackendGameData(BaseModel):
    path: dict[str, str]
    path_r: dict[str, str]
    bds_group: dict[str, BDSGroup]
    logic: BackendLogic
    action_cards: dict[str, dict[str, ActionCardInputModel]]
