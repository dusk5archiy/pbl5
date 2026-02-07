from calc.calc import update_total_ui
from game_data_manager import GAME_DATA
from model.game_state import GameState, Task
from model.game_data import FrontendGameData
from model.chore import PayChore
from calc.mod import (
    mod_action_card,
    mod_release,
    mod_goto_jail,
    mod_buy,
    mod_rent,
)
from pydantic import BaseModel

CaseResult = tuple[GameState, Task | None, bool]


class CaseWrapper(BaseModel):
    game_state: GameState
    new_space: str
    player: str
    steps: int | None = None
    FRONTEND_GAME_DATA: FrontendGameData

    @property
    def default(self):
        return self.game_state, None, False


def case_default(cw: CaseWrapper) -> CaseResult:
    game_state, task = mod_release(cw.game_state)
    return game_state, task, True


def case_pass_BDAU(cw: CaseWrapper) -> CaseResult:
    if cw.new_space != "BDAU":
        return cw.game_state, None, False
    game_state = cw.game_state
    player = cw.player
    game_state.logic.player[player].budget += 200
    return game_state, None, False


def case_land_on_bds(cw: CaseWrapper) -> CaseResult:
    if cw.new_space in cw.FRONTEND_GAME_DATA.bds:
        bds_id = cw.new_space
        if cw.game_state.logic.bds[bds_id].owner is None:
            cw.game_state = mod_buy(cw.game_state, bds_id, cw.player)
        elif (
            cw.game_state.logic.bds[bds_id].level >= 0
            and cw.player != cw.game_state.logic.bds[bds_id].owner
        ):
            cw.game_state = mod_rent(cw.game_state, bds_id, cw.player, cw.steps)
        else:
            cw.game_state, _ = mod_release(cw.game_state)

        return cw.game_state, None, True

    return cw.default


def case_land_on_RA(cw: CaseWrapper) -> CaseResult:
    game_data = GAME_DATA[cw.game_state.version]
    FRONTEND_GAME_DATA = game_data.frontend_game_data
    for bds_id in (
        i for i in FRONTEND_GAME_DATA.bds if FRONTEND_GAME_DATA.bds[i].group == "R"
    ):
        if cw.new_space == bds_id + "A":
            if cw.game_state.logic.bds[bds_id].owner is None:
                cw.game_state = mod_buy(cw.game_state, bds_id, cw.player)
            elif (
                cw.game_state.logic.bds[bds_id].level >= 0
                and cw.player != cw.game_state.logic.bds[bds_id].owner
            ):
                cw.game_state = mod_rent(cw.game_state, bds_id, cw.player, cw.steps)
            else:
                cw.game_state, _ = mod_release(cw.game_state)

            return cw.game_state, None, True

    return cw.default


def case_land_VT(cw: CaseWrapper) -> CaseResult:
    if cw.new_space != "VT":
        return cw.default
    cw.game_state = mod_goto_jail(cw.game_state, cw.player)
    cw.game_state, _ = mod_release(cw.game_state)
    return cw.game_state, None, True


def case_land_TTN(cw: CaseWrapper) -> CaseResult:
    if cw.new_space != "TTN":
        return cw.default

    game_data = GAME_DATA[cw.game_state.version]
    FRONTEND_GAME_DATA = game_data.frontend_game_data
    game_state = cw.game_state
    game_state = update_total_ui(game_state, FRONTEND_GAME_DATA)
    amount = min(200, game_state.ui.player[game_state.logic.current_player].total // 10)
    chore = PayChore(amount=amount, player=cw.player, receiver=None)
    game_state.chore.pay.append(chore)
    game_state, task = mod_release(game_state)
    return game_state, task, True


def case_land_TXX(cw: CaseWrapper) -> CaseResult:
    if cw.new_space != "TXX":
        return cw.default

    game_data = GAME_DATA[cw.game_state.version]
    FRONTEND_GAME_DATA = game_data.frontend_game_data
    game_state = cw.game_state
    game_state = update_total_ui(game_state, FRONTEND_GAME_DATA)
    chore = PayChore(amount=75, player=cw.player, receiver=None)
    game_state.chore.pay.append(chore)
    game_state, task = mod_release(game_state)
    return game_state, task, True


def case_land_on_action_card_space(cw: CaseWrapper) -> CaseResult:
    game_data = GAME_DATA[cw.game_state.version]
    FRONTEND_GAME_DATA = game_data.frontend_game_data
    if cw.new_space not in FRONTEND_GAME_DATA.action:
        return cw.default

    group = FRONTEND_GAME_DATA.action[cw.new_space].group
    cw.game_state = mod_action_card(cw.game_state, group)
    return cw.game_state, None, True


CASE_PASS = [
    case_pass_BDAU,
]

CASE_LAND = [
    case_land_on_bds,
    case_land_on_RA,
    case_land_VT,
    case_land_TTN,
    case_land_TXX,
    case_land_on_action_card_space,
    case_default,
]
