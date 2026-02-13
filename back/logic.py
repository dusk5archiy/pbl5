from model.chore import (
    DiceCChore,
    DiceXbChore,
    EndGameChore,
    GetOutOfJailChore,
    MoveStepsChore,
    PayChore,
    TripleDiceChore,
    Chore,
)
from model.game_state import GameState, Task, TaskResult
from calc.calc import (
    get_double_mode,
    update_action_cards_trade,
    update_action_cards_can,
    update_bds_can,
    update_bds_trade,
)
from calc.prepare_prompt import prepare_pay_prompt
from calc.mod import (
    mod_release,
    mod_goto_jail,
    mod_new_turn,
    mod_pay,
    mod_receive_mortgage,
    mod_auction,
)

from game_data_manager import GAME_DATA

# -----------------------------------------------------------------------------


def generate_states(game_state: GameState, task: Task | None = None):
    game_data = GAME_DATA[game_state.version]
    FRONTEND_GAME_DATA, BACKEND_GAME_DATA = (
        game_data.frontend_game_data,
        game_data.backend_game_data,
    )
    update_bds_can(game_state, FRONTEND_GAME_DATA, BACKEND_GAME_DATA, enable=False)
    update_action_cards_can(game_state, enable=False)
    update_bds_trade(game_state, FRONTEND_GAME_DATA, BACKEND_GAME_DATA, enable=False)
    update_action_cards_trade(game_state, enable=False)
    while task is not None:
        game_state = game_state.__deepcopy__()
        game_state, task = task(game_state)
        if game_state.effect.bds_enabled:
            update_bds_can(game_state, FRONTEND_GAME_DATA, BACKEND_GAME_DATA)
            update_action_cards_can(game_state)

        yield game_state


# -----------------------------------------------------------------------------


class RollDiceTask(Task):
    dice_1: str | None = None
    dice_2: str | None = None

    def __call__(self, game_state: GameState) -> TaskResult:
        assert game_state.current_chore.roll_dice is not None
        game_state.chore.roll_dice.pop(0)
        import random

        player = game_state.logic.current_player

        dice_1 = self.dice_1 or str(random.randint(1, 6))
        dice_2 = self.dice_2 or str(random.randint(1, 6))
        if game_state.version in ["1"]:
            dice_3 = ""
        else:
            dice_3 = random.choice(["1", "2", "3", "c", "c", "xb"])

        double_mode = get_double_mode(dice_1, dice_2, dice_3)

        game_state.effect.dice_1 = str(dice_1)
        game_state.effect.dice_2 = str(dice_2)
        game_state.effect.dice_3 = dice_3

        if double_mode == 3:
            game_state.logic.player[player].double_stack = 0
            new_chore = TripleDiceChore()
            game_state.chore.triple_dice.append(new_chore)
            game_state, task = mod_release(game_state)
            return game_state, task

        else:
            if double_mode == 2:
                game_state.logic.player[player].double_stack += 1
            else:
                game_state.logic.player[player].double_stack = 0
            steps = int(dice_1) + int(dice_2)
            if dice_3.isnumeric():
                steps += int(dice_3)
            elif dice_3 == "c":
                new_chore = DiceCChore()
                game_state.chore.dice_c.append(new_chore)
            elif dice_3 == "xb":
                new_chore = DiceXbChore()
                game_state.chore.dice_xb.append(new_chore)

        game_state.logic.steps = steps
        if game_state.logic.player[player].double_stack == 3:
            game_state = mod_goto_jail(game_state, player)
            game_state, task = mod_release(game_state)
            return game_state, task
        else:
            new_chore = MoveStepsChore(player=player, steps=steps)
            game_state.chore.move_steps.append(new_chore)
            game_state, task = mod_release(game_state)
            return game_state, task


# -----------------------------------------------------------------------------


def mod_buy_bds(game_state: GameState, bds_id: str, player: str, price: int):
    game_state.logic.bds[bds_id].owner = player
    mod_pay(game_state, player, None, price)
    return game_state


class BuyTask(Task):
    response: int

    def __call__(self, game_state: GameState) -> TaskResult:
        assert (chore := game_state.current_chore.buy) is not None
        game_state.chore.buy.pop(0)
        game_state.effect.board = None
        bds_id = chore.bds
        price = chore.price
        player = chore.player

        task = None
        if self.response == 1:
            game_state = mod_buy_bds(game_state, bds_id, player, price)
            game_state.logic.bds[bds_id].level = 0

        elif self.response == 0:
            game_state = mod_auction(game_state, bds_id)

        game_state, task = mod_release(game_state)
        return game_state, task


# -----------------------------------------------------------------------------


class AuctionBdsTask(Task):
    amount: int

    def __call__(self, game_state: GameState) -> TaskResult:
        assert (chore := game_state.current_chore.auction_bds) is not None
        game_state.chore.auction_bds_current.pop(0)
        bds_id = chore.bds
        player = chore.player
        idx = chore.players.index(player)
        next_player = chore.players[(idx + 1) % len(chore.players)]
        chore.player = next_player
        chore.current_price += self.amount

        if self.amount == 0:
            next_players = [p for p in chore.players if p != player]
            chore.players = next_players

        if len(chore.players) > 1:
            game_state.chore.auction_bds_current.append(chore)
        else:
            game_state = mod_buy_bds(
                game_state, bds_id, chore.player, chore.current_price
            )

            if game_state.logic.bds[bds_id].level == -1:
                game_state = mod_receive_mortgage(game_state, next_player, bds_id)

        game_state, task = mod_release(game_state, auction_player=next_player)
        return game_state, task


# -----------------------------------------------------------------------------


class UpgradeTask(Task):
    bds: str

    def __call__(self, game_state: GameState) -> TaskResult:
        bds_state = game_state.logic.bds[self.bds]
        owner = bds_state.owner
        assert owner is not None
        amount = game_state.ui.bds[self.bds].upgrade_amount
        assert amount is not None
        game_data = GAME_DATA[game_state.version]
        FRONTEND_GAME_DATA, BACKEND_GAME_DATA = (
            game_data.frontend_game_data,
            game_data.backend_game_data,
        )

        game_state.logic.bds[self.bds].level += 1
        level = game_state.logic.bds[self.bds].level

        game_state = mod_pay(game_state, owner, None, amount)

        group_id = FRONTEND_GAME_DATA.bds[self.bds].group
        group = BACKEND_GAME_DATA.bds_group[group_id]

        if group.type == 0:
            if 1 <= level <= 4:
                game_state.logic.build.house -= 1
            elif level == 5:
                game_state.logic.build.house += 4
                game_state.logic.build.hotel -= 1
            elif level == 6:
                game_state.logic.build.hotel += 1
                game_state.logic.build.skyscraper -= 1

        game_state.effect.select_bds = None
        game_state.effect.board = None
        return game_state, None


# -----------------------------------------------------------------------------


class DowngradeTask(Task):
    bds: str

    def __call__(self, game_state: GameState) -> TaskResult:
        bds_state = game_state.logic.bds[self.bds]
        owner = bds_state.owner
        assert owner is not None
        amount = game_state.ui.bds[self.bds].downgrade_amount
        assert amount is not None
        game_data = GAME_DATA[game_state.version]
        FRONTEND_GAME_DATA, BACKEND_GAME_DATA = (
            game_data.frontend_game_data,
            game_data.backend_game_data,
        )

        level = game_state.logic.bds[self.bds].level
        game_state.logic.bds[self.bds].level -= 1

        game_state = mod_pay(game_state, None, owner, amount)

        group_id = FRONTEND_GAME_DATA.bds[self.bds].group
        group = BACKEND_GAME_DATA.bds_group[group_id]

        if group.type == 0:
            if 1 <= level <= 4:
                game_state.logic.build.house += 1
            elif level == 5:
                game_state.logic.build.house -= 4
                game_state.logic.build.hotel += 1
            elif level == 6:
                game_state.logic.build.hotel -= 1
                game_state.logic.build.skyscraper += 1

        game_state.effect.select_bds = None
        game_state.effect.board = None
        return game_state, None


# -----------------------------------------------------------------------------


class MortgageTask(Task):
    bds: str

    def __call__(self, game_state: GameState) -> TaskResult:
        bds_state = game_state.logic.bds[self.bds]
        owner = bds_state.owner
        assert owner is not None
        amount = game_state.ui.bds[self.bds].mortgage_amount
        assert amount is not None
        game_state.logic.bds[self.bds].level = -1
        game_state = mod_pay(game_state, None, owner, amount)
        game_state.effect.select_bds = None
        game_state.effect.board = None
        return game_state, None


# -----------------------------------------------------------------------------


class UnmortgageTask(Task):
    bds: str

    def __call__(self, game_state: GameState) -> TaskResult:
        if (
            chore := game_state.current_chore.receive_mortgage
        ) is not None and self.bds == chore.bds:
            new_task = ReceiveMortgageTask(response=1)
            return game_state, new_task

        bds_state = game_state.logic.bds[self.bds]
        owner = bds_state.owner
        assert owner is not None
        amount = game_state.ui.bds[self.bds].unmortgage_amount
        assert amount is not None
        game_state.logic.bds[self.bds].level = 0
        game_state = mod_pay(game_state, owner, None, amount)
        game_state.effect.select_bds = None
        game_state.effect.board = None
        return game_state, None


# -----------------------------------------------------------------------------


class PayTask(Task):
    response: int

    def __call__(self, game_state: GameState) -> TaskResult:
        assert (chore := game_state.current_chore.pay) is not None
        game_state.chore.pay.pop(0)
        game_state.effect.board = None
        assert (player := chore.player) is not None
        then = chore.then
        amount = chore.amount
        receiver = chore.receiver
        if self.response == 1:
            game_state = mod_pay(game_state, player, receiver, amount)
            game_state, new_task = mod_release(game_state, then=then)
            return game_state, new_task
        else:
            new_task = BankruptTask(loser=player, winner=receiver)
            return game_state, new_task


# -----------------------------------------------------------------------------


class ReceiveMortgageTask(Task):
    response: int

    def __call__(self, game_state: GameState) -> TaskResult:
        assert (chore := game_state.current_chore.receive_mortgage) is not None
        game_state.chore.receive_mortgage.pop(0)
        player = chore.player
        if self.response == 0:
            new_task = BankruptTask(loser=player)
            return game_state, new_task

        if self.response == 1:
            amount = chore.unmortgage
            game_state.logic.bds[chore.bds].level = 0
        else:
            amount = chore.interest

        game_state = mod_pay(game_state, player, None, amount)
        game_state, task = mod_release(game_state, auction_player=player)
        return game_state, task


# -----------------------------------------------------------------------------


class EndTurnTask(Task):
    def __call__(self, game_state: GameState) -> TaskResult:
        assert (chore := game_state.current_chore.end_turn) is not None

        game_state.turns += 1
        players_alive = [
            p for p in game_state.logic.player if game_state.logic.player[p].alive
        ]

        num_alive = len(players_alive)

        if num_alive <= 1:
            return game_state, EndGameTask()

        current_player = game_state.logic.current_player
        players = [
            p
            for p in game_state.logic.player_order
            if p == current_player or p in players_alive
        ]

        if chore.next_player:
            game_state.logic.player[current_player].double_stack = 0
            idx = players.index(current_player)
            next_player = players[(idx + 1) % len(players)]
        else:
            next_player = current_player
        game_state = mod_new_turn(game_state, next_player)
        return game_state, None


# -----------------------------------------------------------------------------


class JailTask(Task):
    response: int
    dice_1: str | None = None
    dice_2: str | None = None

    def __call__(self, game_state: GameState) -> TaskResult:
        assert (chore := game_state.current_chore.jail) is not None
        game_state.chore.jail.pop(0)

        player = game_state.logic.current_player

        task = None
        if self.response == 0:
            import random

            dice_1 = self.dice_1 or str(random.randint(1, 6))
            dice_2 = self.dice_2 or str(random.randint(1, 6))
            steps = int(dice_1) + int(dice_2)
            game_state.logic.steps = steps
            game_state.effect.dice_1 = str(dice_1)
            game_state.effect.dice_2 = str(dice_2)
            game_state.effect.dice_3 = None

            game_state.chore.roll_dice.pop(0)
            if dice_1 == dice_2:
                game_state.logic.player[player].at = "TT"
                game_state.logic.player[player].jail_stack = 0
                new_chore = MoveStepsChore(steps=steps, player=player)
                game_state.chore.move_steps.append(new_chore)
            elif game_state.logic.player[player].jail_stack == 3:
                prepare_pay_prompt(game_state, player)
                new_chore = PayChore(
                    amount=chore.amount,
                    player=player,
                    receiver=None,
                    then=Chore(
                        get_out_of_jail=[
                            GetOutOfJailChore(
                                player=player,
                                then=Chore(
                                    move_steps=[
                                        MoveStepsChore(player=player, steps=steps)
                                    ]
                                ),
                            )
                        ]
                    ),
                )
                game_state.chore.pay.append(new_chore)
            else:
                game_state.logic.player[player].jail_stack += 1
            game_state, task = mod_release(game_state)

        elif self.response == 1:
            prepare_pay_prompt(game_state, player)
            new_chore = PayChore(
                amount=chore.amount,
                player=player,
                receiver=None,
                then=Chore(get_out_of_jail=[GetOutOfJailChore(player=player)]),
            )
            game_state.chore.pay.append(new_chore)
            game_state, task = mod_release(game_state)
        return game_state, task


# -----------------------------------------------------------------------------


class BankruptTask(Task):
    loser: str
    winner: str | None = None

    def __call__(self, game_state: GameState) -> TaskResult:
        game_data = GAME_DATA[game_state.version]
        FRONTEND_GAME_DATA = game_data.frontend_game_data
        loser, winner = self.loser, self.winner
        game_state.logic.player[loser].alive = False
        game_state.chore.receive_mortgage = [
            c for c in game_state.chore.receive_mortgage if c.player != loser
        ]
        game_state.chore.pay = [
            c for c in game_state.chore.pay if c.player != loser and c.receiver != loser
        ]
        game_state.logic.player[loser].double_stack = 0
        game_state.chore.dice_c.clear()
        game_state.chore.dice_xb.clear()
        loser_budget = game_state.logic.player[loser].budget
        game_state.logic.player[loser].budget = 0
        players_alive = [
            p for p in game_state.logic.player_order if game_state.logic.player[p].alive
        ]
        num_alive = len(players_alive)
        normal_bds = [
            bds_id
            for bds_id in game_state.logic.bds
            if game_state.logic.bds[bds_id].owner == loser
            and game_state.logic.bds[bds_id].level >= 0
        ]

        mortgaged_bds = [
            bds_id
            for bds_id in game_state.logic.bds
            if game_state.logic.bds[bds_id].owner == loser
            and game_state.logic.bds[bds_id].level == -1
        ]
        if winner is not None:
            add_budget = loser_budget

            for bds_id in normal_bds:
                game_state.logic.bds[bds_id].owner = winner
                level = game_state.logic.bds[bds_id].level
                if (downgrade := FRONTEND_GAME_DATA.bds[bds_id].downgrade) is not None:
                    add_budget += level * downgrade
                game_state.logic.bds[bds_id].level = 0

            for bds_id in mortgaged_bds:
                game_state.logic.bds[bds_id].owner = winner

            game_state.logic.player[winner].budget += add_budget

            bds_left = mortgaged_bds
            if len(bds_left) > 0:
                for bds in bds_left:
                    game_state = mod_receive_mortgage(game_state, winner, bds)

            game_state, task = mod_release(game_state)

        elif num_alive > 1:
            for bds_id in normal_bds:
                game_state.logic.bds[bds_id].level = 0

            bds_left = [
                bds_id
                for bds_id in game_state.logic.bds
                if game_state.logic.bds[bds_id].owner == loser
            ]
            if len(bds_left) > 0:
                players = [
                    p
                    for p in game_state.logic.player_order
                    if game_state.logic.player[p].alive or p == loser
                ]
                idx = players.index(loser)
                next_player = players[(idx + 1) % len(players)]
                for bds in bds_left:
                    game_state = mod_auction(game_state, bds)
                game_state, task = mod_release(game_state, auction_player=next_player)
            else:
                game_state, task = mod_release(game_state)

        elif num_alive == 1:
            winner = players_alive[0]
            for bds_id in normal_bds:
                game_state.logic.bds[bds_id].owner = winner
                game_state.logic.bds[bds_id].level = 0

            for bds_id in mortgaged_bds:
                game_state.logic.bds[bds_id].owner = winner

            bds_left = mortgaged_bds
            if len(bds_left) > 0:
                for bds in bds_left:
                    game_state = mod_receive_mortgage(game_state, winner, bds)

            game_state, task = mod_release(game_state)
        else:
            task = EndGameTask()

        return game_state, task


# -----------------------------------------------------------------------------


class EndGameTask(Task):
    def __call__(self, game_state: GameState) -> TaskResult:
        players_alive = [
            p for p in game_state.logic.player if game_state.logic.player[p].alive
        ]
        player_order = sorted(
            players_alive, key=lambda p: game_state.ui.player[p].total, reverse=True
        )
        new_chore = EndGameChore(player_order=player_order)
        game_state.chore = Chore(end_game=[new_chore])
        game_state, task = mod_release(game_state)
        return game_state, task


# -----------------------------------------------------------------------------
