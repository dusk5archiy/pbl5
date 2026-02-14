from calc.mod import mod_pay, mod_receive_mortgage, mod_release
from model.chore import StartTradeChore, TradeCard, TradeChore, TradeItem
from model.game_data import FrontendGameData
from model.game_state import GameState, Task, TaskResult
from game_data_manager import GAME_DATA
from calc.calc import get_bds_total_price


# -----------------------------------------------------------------------------


class StartTradeTask(Task):
    def __call__(self, game_state: GameState) -> TaskResult:
        player = game_state.logic.current_player
        players = [
            p
            for p in game_state.logic.player
            if game_state.logic.player[p].alive and p != player
        ]
        new_chore = StartTradeChore(player=player, players=players)
        game_state.chore.start_trade.append(new_chore)
        game_state, task = mod_release(game_state)
        return game_state, task


# -----------------------------------------------------------------------------


def calc_trade_item_total(
    game_state: GameState, FRONTEND_GAME_DATA: FrontendGameData, item: TradeItem
):
    item.total = item.money
    for bds in item.bds:
        item.total += get_bds_total_price(game_state, FRONTEND_GAME_DATA, bds)

    return item


# -----------------------------------------------------------------------------


class TradeTask(Task):
    player_2: str | None = None
    bds: str | None = None
    card: TradeCard | None = None
    money_1: int | None = None
    money_2: int | None = None
    response: int | None = None

    def __call__(self, game_state: GameState) -> TaskResult:
        game_data = GAME_DATA[game_state.version]
        FRONTEND_GAME_DATA = game_data.frontend_game_data
        if game_state.current_chore.start_trade is not None:
            player = game_state.logic.current_player
            assert (player_2 := self.player_2) is not None
            game_state.chore.start_trade.pop(0)
            new_chore = TradeChore(player=player, player_1=player, player_2=player_2)
            game_state.chore.trade.append(new_chore)
            game_state, task = mod_release(game_state)
            return game_state, task
        elif (chore := game_state.current_chore.trade) is not None:

            def append():
                chore.player_1_item = calc_trade_item_total(
                    game_state, FRONTEND_GAME_DATA, chore.player_1_item
                )
                chore.player_2_item = calc_trade_item_total(
                    game_state, FRONTEND_GAME_DATA, chore.player_2_item
                )
                game_state.chore.trade.append(chore)

            game_state.chore.trade.pop(0)
            player_1 = chore.player_1
            player_2 = chore.player_2

            if (bds := self.bds) is not None:
                owner = game_state.logic.bds[bds].owner
                if owner == player_1:
                    if bds in chore.player_1_item.bds:
                        chore.player_1_item.bds.remove(bds)
                    else:
                        chore.player_1_item.bds.append(bds)
                elif owner == player_2:
                    if bds in chore.player_2_item.bds:
                        chore.player_2_item.bds.remove(bds)
                    else:
                        chore.player_2_item.bds.append(bds)
                chore.player_1_item = calc_trade_item_total(
                    game_state, FRONTEND_GAME_DATA, chore.player_1_item
                )
                chore.player_2_item = calc_trade_item_total(
                    game_state, FRONTEND_GAME_DATA, chore.player_2_item
                )
                append()

            elif self.card is not None:
                group, card = self.card.group, self.card.card
                owner = game_state.logic.action[group][card].owner
                c = TradeCard(group=group, card=card)
                if owner == player_1:
                    if c in chore.player_1_item.card:
                        chore.player_1_item.card.remove(c)
                    else:
                        chore.player_1_item.card.append(c)
                elif owner == player_2:
                    if c in chore.player_2_item.card:
                        chore.player_2_item.card.remove(c)
                    else:
                        chore.player_2_item.card.append(c)
                append()

            elif (money_1 := self.money_1) is not None:
                if money_1 > 0:
                    chore.player_1_item.money = min(
                        game_state.logic.budget[player_1],
                        chore.player_1_item.money + money_1,
                    )
                else:
                    chore.player_1_item.money = money_1
                append()

            elif (money_2 := self.money_2) is not None:
                if money_2 > 0:
                    chore.player_2_item.money = min(
                        game_state.logic.budget[player_2],
                        chore.player_2_item.money + money_2,
                    )
                else:
                    chore.player_2_item.money = money_2
                append()
            elif (response := self.response) is not None:
                if response == 0:
                    pass
                elif response == 1 and not chore.confirm_mode:
                    chore.confirm_mode = True
                    chore.player = player_2 if chore.player != player_2 else player_1
                    game_state.chore.trade.append(chore)
                elif response == 2 and chore.confirm_mode:
                    chore.confirm_mode = False
                    game_state.chore.trade.append(chore)

                elif response == 1 and chore.confirm_mode:
                    money_1 = chore.player_1_item.money
                    money_2 = chore.player_2_item.money
                    mod_pay(game_state, sender=player_1, receiver=None, amount=money_1)
                    mod_pay(game_state, sender=player_2, receiver=None, amount=money_2)
                    mod_pay(game_state, sender=None, receiver=player_1, amount=money_2)
                    mod_pay(game_state, sender=None, receiver=player_2, amount=money_1)
                    for bds in chore.player_2_item.bds:
                        game_state.logic.bds[bds].owner = player_1
                        game_state = mod_receive_mortgage(game_state, player_1, bds)
                    for bds in chore.player_1_item.bds:
                        game_state.logic.bds[bds].owner = player_2
                        game_state = mod_receive_mortgage(game_state, player_2, bds)
                    for c in chore.player_1_item.card:
                        group, card = c.group, c.card
                        game_state.logic.action[group][card].owner = player_2
                    for c in chore.player_2_item.card:
                        group, card = c.group, c.card
                        game_state.logic.action[group][card].owner = player_1

        game_state, task = mod_release(game_state)
        return game_state, task


# -----------------------------------------------------------------------------
