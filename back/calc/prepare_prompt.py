from model.game_state import GameState


def prepare_pay_prompt(
    game_state: GameState, player: str, bds: str | None = None
) -> GameState:
    game_state.effect.bds_enabled = True
    game_state.logic.viewing_player = player
    game_state.effect.wait_ms = 0
    if bds is not None:
        game_state.effect.select_bds = bds

    return game_state


def prepare_dice(game_state: GameState):
    game_state.effect.dice_1 = None
    game_state.effect.dice_2 = None
    game_state.effect.dice_3 = None
    return game_state


def prepare_two_dice_rent_u_prompt(game_state: GameState, player: str) -> GameState:
    game_state = prepare_pay_prompt(game_state, player)
    game_state = prepare_dice(game_state)
    return game_state


def prepare_roll_dice_prompt(game_state: GameState):
    game_state = prepare_dice(game_state)
    return game_state


def prepare_jail_prompt(game_state: GameState):
    game_state = prepare_dice(game_state)
    return game_state
