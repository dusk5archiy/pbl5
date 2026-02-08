from calc.prepare_prompt import (
    prepare_pay_prompt,
    prepare_two_dice_rent_u_prompt,
    prepare_roll_dice_prompt,
    prepare_jail_prompt,
)
from model.chore import (
    AuctionBdsChore,
    AuctionBdsCurrentChore,
    Chore,
    BuyChore,
    CurrentChore,
    PayChore,
    JailChore,
    ReceiveMortgageChore,
    RollDiceChore,
    ActionCardChore,
    EndTurnChore,
    TwoDiceRentUChore,
)
from model.game_state import GameState, TaskResult
from game_data_manager import GAME_DATA
from calc.calc import get_rent

# -----------------------------------------------------------------------------


def mod_reset_card_effects(game_state: GameState):
    game_state.logic.rent_multiplier = 1
    game_state.logic.u_multiplier = None
    return game_state


def mod_reset_dice_effects(game_state: GameState):
    game_state.chore.dice_c.clear()
    game_state.chore.dice_xb.clear()
    return game_state


def mod_reset(game_state: GameState):
    game_state = mod_reset_card_effects(game_state)
    game_state = mod_reset_dice_effects(game_state)
    return game_state


# -----------------------------------------------------------------------------


def mod_intermediate(game_state: GameState):
    game_state.current_chore = CurrentChore()
    return game_state


def mod_release(
    game_state: GameState, then: Chore | None = None, auction_player: str | None = None
) -> TaskResult:
    new_task = None
    game_state.current_chore = CurrentChore()
    while True:
        if then is None:
            then = game_state.chore
        if len(chores := then.move_steps) > 0:
            from task.move import MoveStepsTask

            chore = chores.pop(0)
            game_state = MoveStepsTask.prepare(game_state)
            new_task = MoveStepsTask.from_steps(player=chore.player, steps=chore.steps)
            break

        if len(chores := then.get_out_of_jail) > 0:
            chore = chores.pop(0)
            then = chore.then
            game_state = mod_get_outof_jail(game_state, player=chore.player)
            continue

        game_state.effect.wait_ms = 0

        if len(chores := then.receive_mortgage) > 0:
            chore = chores[0]
            game_state.current_chore.receive_mortgage = chore
            game_state.effect.bds_enabled = True
            game_state.effect.can_trade = False
            game_state.logic.viewing_player = chore.player
            break

        if len(chores := then.auction_bds_current) > 0:
            chore = chores[0]
            game_state.current_chore.auction_bds = chore
            game_state.effect.bds_enabled = False
            game_state.effect.can_trade = False
            game_state.logic.viewing_player = chore.player
            break

        if len(chores := then.auction_bds) > 0:
            auction_player = auction_player or game_state.logic.current_player
            chore = chores.pop(0)
            alive_players = [
                p for p in game_state.logic.player if game_state.logic.player[p].alive
            ]

            current_chore = AuctionBdsCurrentChore(
                original_price=chore.original_price,
                current_price=0,
                bds=chore.bds,
                player=auction_player,
                players=alive_players,
            )
            game_state.chore.auction_bds_current.append(current_chore)
            game_state.effect.select_bds = chore.bds
            continue

        if len(chores := then.end_game) > 0:
            chore = chores[0]
            game_state.current_chore.end_game = chore
            game_state.effect.bds_enabled = False
            game_state.effect.can_trade = False
            break

        if len(chores := then.pay) > 0:
            chore = chores[0]
            game_state.current_chore.pay = chore
            game_state.effect.bds_enabled = True
            game_state.effect.can_trade = False
            game_state.logic.viewing_player = chore.player
            if chore.bds is not None:
                game_state.effect.select_bds = chore.bds
            break

        if len(chores := then.buy) > 0:
            chore = chores[0]
            game_state.current_chore.buy = chore

            game_state.logic.viewing_player = chore.player
            game_state.effect.select_bds = chore.bds
            game_state.effect.bds_enabled = False
            game_state.effect.can_trade = False
            break

        if len(chores := then.action_card) > 0:
            chore = chores[0]
            game_state.current_chore.action_card = chore
            game_state.effect.bds_enabled = False
            game_state.effect.can_trade = False
            break

        if len(chores := then.triple_dice) > 0:
            chore = chores[0]
            game_state.current_chore.triple_dice = chore
            game_state.effect.bds_enabled = False
            game_state.effect.can_trade = False
            break

        if len(chores := then.start_trade) > 0:
            chore = chores[0]
            game_state.current_chore.start_trade = chore

            game_state.logic.viewing_player = chore.player
            game_state.effect.bds_enabled = False
            game_state.effect.can_trade = False
            game_state.effect.board = None
            break

        if len(chores := then.two_dice_rent_u) > 0:
            chore = chores[0]
            game_state.current_chore.two_dice_rent_u = chore

            game_state.logic.viewing_player = chore.player
            game_state.effect.bds_enabled = False
            game_state.effect.can_trade = False
            game_state.effect.board = None
            break

        if len(chores := then.trade) > 0:
            chore = chores[0]
            game_state.current_chore.trade = chore

            game_state.logic.viewing_player = chore.player
            game_state.effect.bds_enabled = False
            game_state.effect.can_trade = False
            game_state.effect.board = None
            break

        game_state = mod_reset_card_effects(game_state)
        game_state.logic.viewing_player = None
        game_state.effect.select_bds = None
        player = game_state.logic.current_player
        if game_state.logic.player[player].alive:
            game_state.effect.bds_enabled = True
            game_state.effect.can_trade = True
        else:
            game_state.effect.bds_enabled = False
            game_state.effect.can_trade = False

        if len(chores := then.jail) > 0:
            game_state.current_chore.jail = chores[0]
        elif len(chores := then.roll_dice) > 0:
            game_state.current_chore.roll_dice = chores[0]
        elif len(chores := then.dice_c) > 0:
            game_state.current_chore.dice_c = chores[0]
        elif len(chores := then.dice_xb) > 0:
            game_state.current_chore.dice_xb = chores[0]
        else:
            game_state.effect.board = None
            game_state.current_chore.end_turn = EndTurnChore(
                player=player,
                next_player=(game_state.logic.player[player].double_stack in [0, 3]),
            )
        break
    return game_state, new_task


# -----------------------------------------------------------------------------


def mod_new_turn(game_state: GameState, next_player: str):
    game_data = GAME_DATA[game_state.version]
    FRONTEND_GAME_DATA = game_data.frontend_game_data
    next_at = game_state.logic.player[next_player].at
    next_player_board = (
        FRONTEND_GAME_DATA.space[next_at].board
        if next_at in FRONTEND_GAME_DATA.space
        else FRONTEND_GAME_DATA.special_space[next_at].board
    )

    game_state.logic.current_player = next_player
    game_state.effect.board = next_player_board
    game_state.effect.select_bds = None
    game_state.effect.movement_lines.clear()
    game_state.effect.bds_enabled = True
    game_state.effect.can_trade = True

    game_state = mod_reset(game_state)
    game_state.logic.steps = None

    game_state = prepare_roll_dice_prompt(game_state)
    game_state.chore.roll_dice.append(RollDiceChore())
    if game_state.logic.player[next_player].jail_stack > 0:
        game_state = prepare_jail_prompt(game_state)
        game_state.chore.jail.append(JailChore(amount=50))
    game_state, _ = mod_release(game_state)
    return game_state


# -----------------------------------------------------------------------------


def mod_auction(game_state: GameState, bds: str):
    game_data = GAME_DATA[game_state.version]
    FRONTEND_GAME_DATA = game_data.frontend_game_data
    original_price = FRONTEND_GAME_DATA.bds[bds].price
    chore = AuctionBdsChore(
        original_price=original_price,
        bds=bds,
    )
    game_state.chore.auction_bds.append(chore)
    return game_state


# -----------------------------------------------------------------------------


def mod_receive_mortgage(game_state: GameState, player: str, bds: str):
    if game_state.logic.bds[bds].level != -1:
        return game_state
    game_data = GAME_DATA[game_state.version]
    FRONTEND_GAME_DATA = game_data.frontend_game_data
    unmortgage = FRONTEND_GAME_DATA.bds[bds].unmortgage
    interest = unmortgage - FRONTEND_GAME_DATA.bds[bds].mortgage
    chore = ReceiveMortgageChore(
        player=player,
        bds=bds,
        unmortgage=unmortgage,
        interest=interest,
    )
    game_state.chore.receive_mortgage.append(chore)
    return game_state


# -----------------------------------------------------------------------------


def mod_move(game_state: GameState):
    game_state.effect.can_trade = False
    game_state.effect.bds_enabled = False
    game_state.effect.wait_ms = 0
    return game_state


# -----------------------------------------------------------------------------


def mod_buy(game_state: GameState, bds: str, player: str):
    game_data = GAME_DATA[game_state.version]
    FRONTEND_GAME_DATA = game_data.frontend_game_data
    price = FRONTEND_GAME_DATA.bds[bds].price
    chore = BuyChore(
        player=player,
        bds=bds,
        price=price,
    )
    game_state.chore.buy.append(chore)
    game_state, _ = mod_release(game_state)
    return game_state


# -----------------------------------------------------------------------------


def mod_rent(
    game_state: GameState,
    bds: str,
    player: str,
    steps: int | None = None,
):
    game_data = GAME_DATA[game_state.version]
    FRONTEND_GAME_DATA, BACKEND_GAME_DATA = (
        game_data.frontend_game_data,
        game_data.backend_game_data,
    )
    info = FRONTEND_GAME_DATA.bds[bds]

    if info.group == "U" and game_state.logic.u_multiplier is not None:
        game_state = prepare_two_dice_rent_u_prompt(game_state, player)
        chore = TwoDiceRentUChore(bds=bds, player=player)
        game_state.chore.two_dice_rent_u.append(chore)
        return game_state

    amount = (
        get_rent(game_state, FRONTEND_GAME_DATA, BACKEND_GAME_DATA, bds, steps)
        * game_state.logic.rent_multiplier
    )

    if amount > 0:
        owner = game_state.logic.bds[bds].owner
        game_state = prepare_pay_prompt(game_state, player)
        chore = PayChore(bds=bds, amount=amount, player=player, receiver=owner)
        game_state.chore.pay.append(chore)

    game_state, _ = mod_release(game_state)
    return game_state


# -----------------------------------------------------------------------------


def mod_pay(
    game_state: GameState, sender: str | None, receiver: str | None, amount: int
):
    if sender is not None:
        assert game_state.logic.player[sender].budget >= amount
        game_state.logic.player[sender].budget -= amount
    if receiver is not None:
        game_state.logic.player[receiver].budget += amount
    return game_state


# -----------------------------------------------------------------------------


def mod_goto_jail(game_state: GameState, player: str):
    if game_state.logic.current_player == player:
        game_state = mod_reset(game_state)
    game_state.chore.roll_dice.clear()
    player_state = game_state.logic.player[player]
    player_state.double_stack = 0
    player_state.jail_stack = 1
    player_state.at = "OT"
    game_state.logic.player[player] = player_state
    return game_state


# -----------------------------------------------------------------------------


def mod_get_outof_jail(game_state: GameState, player: str):
    game_state.logic.player[player].at = "TT"
    game_state.logic.player[player].jail_stack = 0
    return game_state


# -----------------------------------------------------------------------------


def mod_action_card(game_state: GameState, group: str):
    # If there is no card left, return.
    if len(game_state.logic.action_card[group]) == 0:
        game_state, _ = mod_release(game_state)
        return game_state

    card = game_state.logic.action_card[group].pop(0)
    new_chore = ActionCardChore(group=group, card=card)
    game_state.chore.action_card.append(new_chore)
    game_state, _ = mod_release(game_state)
    return game_state


# -----------------------------------------------------------------------------
