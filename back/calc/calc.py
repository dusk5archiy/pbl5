from model.game_state import (
    GameState,
    UiStatePlayer,
    MovementLine,
)
from model.game_data import FrontendGameData, BackendGameData
from typing import Callable

# -----------------------------------------------------------------------------


def calc_new_space(
    game_state: GameState,
    current_space: str,
    FRONTEND_GAME_DATA: FrontendGameData,
    BACKEND_GAME_DATA: BackendGameData,
    check_last_space: Callable[[str], bool],
    change_track_on_cau: bool = False,
    change_track_on_r: bool = False,
    draw_movement_lines: bool = False,
    reversed: bool = False,
):
    cau_s = ["CAU-1", "CAU-2"]
    path = BACKEND_GAME_DATA.path_r if reversed else BACKEND_GAME_DATA.path
    new_space = path[current_space]
    if change_track_on_cau and current_space in cau_s:
        idx = cau_s.index(current_space)
        new_space = path[cau_s[(idx + 1) % len(cau_s)]]
    elif change_track_on_r:
        for this in BACKEND_GAME_DATA.bds_group["R"].bds:
            if (that := this + "A") in FRONTEND_GAME_DATA.space:
                if current_space == this:
                    new_space = path[that]
                    break
                elif current_space == that:
                    new_space = path[this]
                    break
            elif current_space == this:
                new_space = path[this]
                break

    if draw_movement_lines:
        current_board = FRONTEND_GAME_DATA.space[current_space].board
        new_board = FRONTEND_GAME_DATA.space[new_space].board
        if current_board == new_board:
            game_state.effect.movement_lines.append(
                MovementLine(
                    arrow=check_last_space(new_space),
                    start=current_space,
                    end=new_space,
                )
            )
    return new_space


# -----------------------------------------------------------------------------


def get_double_mode(dice_1: str, dice_2: str, dice_3: str | None):
    if dice_3 is not None and dice_1 == dice_2 and dice_2 == dice_3:
        return 3

    if dice_1 == dice_2:
        return 2

    return 1


# -----------------------------------------------------------------------------


def update_bds_level(
    game_state: GameState,
    FRONTEND_GAME_DATA: FrontendGameData,
    BACKEND_GAME_DATA: BackendGameData,
):
    viewing_player = game_state.logic.viewing_player or game_state.logic.current_player
    for bds_id in FRONTEND_GAME_DATA.bds:
        owner = game_state.logic.bds[bds_id].owner

        ui_bds = game_state.ui.bds[bds_id]

        bds = FRONTEND_GAME_DATA.bds[bds_id]
        bds_state = game_state.logic.bds[bds_id]
        level = bds_state.level
        group_id = bds.group
        group = BACKEND_GAME_DATA.bds_group[group_id]

        owner_owned_bds = [
            b for b in group.bds if game_state.logic.bds[b].owner == owner
        ]

        if group.type == 1 and bds_state.level >= 0 and owner is not None:
            ui_bds.level = level + len(owner_owned_bds)
        else:
            ui_bds.level = level

        if owner == viewing_player:
            ui_bds.upgrade_amount = bds.upgrade
            ui_bds.downgrade_amount = bds.downgrade
            ui_bds.mortgage_amount = bds.mortgage
            ui_bds.unmortgage_amount = bds.unmortgage

        game_state.ui.bds[bds_id] = ui_bds
    return game_state


def update_bds_can(
    game_state: GameState,
    FRONTEND_GAME_DATA: FrontendGameData,
    BACKEND_GAME_DATA: BackendGameData,
    enable: bool = True,
):
    viewing_player = game_state.logic.viewing_player or game_state.logic.current_player
    for bds_id in FRONTEND_GAME_DATA.bds:
        ui_bds = game_state.ui.bds[bds_id]
        if not enable:
            ui_bds.can_upgrade = False
            ui_bds.can_downgrade = False
            ui_bds.can_mortgage = False
            ui_bds.can_unmortgage = False
            game_state.ui.bds[bds_id] = ui_bds
            continue

        owner = game_state.logic.bds[bds_id].owner

        bds = FRONTEND_GAME_DATA.bds[bds_id]
        bds_state = game_state.logic.bds[bds_id]
        level = bds_state.level
        group_id = bds.group
        group = BACKEND_GAME_DATA.bds_group[group_id]

        owner_owned_bds = [
            b for b in group.bds if game_state.logic.bds[b].owner == owner
        ]
        owned_bds_level = [game_state.logic.bds[b].level for b in owner_owned_bds]

        if owner == viewing_player:
            unmortgage_amount = bds.unmortgage
            ui_bds.can_unmortgage = (
                level == -1
                and game_state.logic.player[viewing_player].budget >= unmortgage_amount
            )
            if group.type == 1:
                ui_bds.can_mortgage = bds_state.level == 0
                ui_bds.can_upgrade = bds.upgrade is not None and bds_state.level == 0
                ui_bds.can_downgrade = bds_state.level > 0 and bds.downgrade is not None
            else:
                major = len(owner_owned_bds) == len(group.bds)
                minor = (
                    len(owner_owned_bds) > len(group.bds) // 2
                    if game_state.version not in ["1"]
                    else major
                )
                ui_bds.can_mortgage = bds_state.level == 0 and all(
                    n in [0, -1] for n in owned_bds_level
                )

                if (
                    (minor and 0 <= level <= 3 and game_state.logic.build.house >= 1)
                    or (
                        5 < len(bds.rent)
                        and minor
                        and level == 4
                        and game_state.logic.build.hotel >= 1
                    )
                    or (
                        game_state.version not in ["1"]
                        and 6 < len(bds.rent)
                        and major
                        and level == 5
                        and game_state.logic.build.skyscraper >= 1
                    )
                ) and all(n in [level, level + 1] for n in owned_bds_level):
                    ui_bds.can_upgrade = True

                if (
                    (1 <= level <= 4)
                    or (level == 5 and game_state.logic.build.house >= 4)
                    or (level == 6 and game_state.logic.build.hotel >= 1)
                ) and all(n in [level - 1, level] for n in owned_bds_level):
                    ui_bds.can_downgrade = True

        game_state.ui.bds[bds_id] = ui_bds
    return game_state


def update_bds_trade(
    game_state: GameState,
    FRONTEND_GAME_DATA: FrontendGameData,
    BACKEND_GAME_DATA: BackendGameData,
    enable: bool = True,
):
    trade_chore = game_state.current_chore.trade
    for bds_id in FRONTEND_GAME_DATA.bds:
        if trade_chore is None or not enable:
            game_state.ui.bds[bds_id].can_choose = False
            continue

        owner = game_state.logic.bds[bds_id].owner

        bds = FRONTEND_GAME_DATA.bds[bds_id]
        group_id = bds.group
        group = BACKEND_GAME_DATA.bds_group[group_id]

        owner_owned_bds = [
            b for b in group.bds if game_state.logic.bds[b].owner == owner
        ]
        owned_bds_level = [game_state.logic.bds[b].level for b in owner_owned_bds]
        player_1, player_2 = trade_chore.player_1, trade_chore.player_2
        game_state.ui.bds[bds_id].can_choose = (
            not trade_chore.confirm_mode
            and owner in [player_1, player_2]
            and (
                group.type == 1
                or (group.type == 0 and all(n in [0, -1] for n in owned_bds_level))
            )
        )
    return game_state


# -----------------------------------------------------------------------------


def get_bds_total_price(
    game_state: GameState, FRONTEND_GAME_DATA: FrontendGameData, bds_id: str
):
    owner = game_state.logic.bds[bds_id].owner
    if owner is None:
        return 0

    bds = FRONTEND_GAME_DATA.bds[bds_id]
    bds_state = game_state.logic.bds[bds_id]
    level = bds_state.level

    total = 0
    if level >= 0:
        total += bds.price
        if bds.upgrade is not None and level > 0:
            total += bds.upgrade * level
    else:
        total = bds.price - bds.mortgage

    return total


# -----------------------------------------------------------------------------


def update_total_ui(
    game_state: GameState,
    FRONTEND_GAME_DATA: FrontendGameData,
):
    game_state.ui.player = {
        p: UiStatePlayer(total=game_state.logic.player[p].budget)
        for p in game_state.logic.player
    }
    for bds_id in game_state.logic.bds:
        owner = game_state.logic.bds[bds_id].owner
        if owner is None:
            continue

        game_state.ui.player[owner].total += get_bds_total_price(
            game_state, FRONTEND_GAME_DATA, bds_id
        )

    return game_state


# -----------------------------------------------------------------------------


def update_action_cards_can(game_state: GameState, enable: bool = True):
    for group in game_state.logic.action:
        for card_id in game_state.logic.action[group]:
            if not enable:
                game_state.ui.action[group][card_id].can_use = False
                continue
            state = game_state.logic.action[group][card_id]
            owner = state.owner
            if owner is None:
                continue
            player = game_state.logic.current_player
            game_state.ui.action[group][card_id].can_use = enable and (
                card_id == "TDRT"
                and player == owner
                and game_state.current_chore.jail is not None
            )
    return game_state


def update_action_cards_trade(game_state: GameState, enable: bool = True):
    trade_chore = game_state.current_chore.trade
    for group in game_state.logic.action:
        for card_id in game_state.logic.action[group]:
            if trade_chore is None or not enable:
                game_state.ui.action[group][card_id].can_choose = False
                continue
            state = game_state.logic.action[group][card_id]
            owner = state.owner
            if owner is None:
                continue
            player_1 = trade_chore.player_1
            player_2 = trade_chore.player_2
            game_state.ui.action[group][card_id].can_choose = (
                not trade_chore.confirm_mode
                and owner
                in [
                    player_1,
                    player_2,
                ]
            )
    return game_state


# -----------------------------------------------------------------------------


def get_rent(
    game_state: GameState,
    FRONTEND_GAME_DATA: FrontendGameData,
    BACKEND_GAME_DATA: BackendGameData,
    bds_id: str,
    steps: int | None = None,
) -> int:
    bds_state = game_state.logic.bds[bds_id]
    bds = FRONTEND_GAME_DATA.bds[bds_id]
    owner = game_state.logic.bds[bds_id].owner
    if owner is None or bds_state.level == -1:
        return 0

    group_id = bds.group
    group = BACKEND_GAME_DATA.bds_group[group_id]
    group_bds = group.bds
    owned_group_bds = [b for b in group.bds if game_state.logic.bds[b].owner == owner]
    num_owned = len(owned_group_bds)
    num_in_group = len(group_bds)

    rent = 0
    if group_id == "U" and steps is not None:
        level = bds_state.level - 1 + num_owned
        rent = FRONTEND_GAME_DATA.bds[bds_id].rent[level] * steps
    elif group.type == 1:
        rent = FRONTEND_GAME_DATA.bds[bds_id].rent[num_owned - 1 + bds_state.level]

    elif group.type == 0:
        level = bds_state.level
        rent = FRONTEND_GAME_DATA.bds[bds_id].rent[level]
        if level == 0:
            if num_owned == num_in_group:
                rent *= 3
            elif num_owned > num_in_group // 2:
                rent *= 2

    return rent


# -----------------------------------------------------------------------------
