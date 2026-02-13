from calc.prepare_prompt import prepare_pay_prompt, prepare_roll_dice_prompt
from model.chore import RollDiceChore, PayChore, GotoJailChore
from model.game_state import GameState, Task, TaskResult
from game_data_manager import GAME_DATA
from calc.mod import (
    mod_get_outof_jail,
    mod_pay,
    mod_release,
)
from task.dice import MoveToSpaceTask
from task.move import MoveNearestTask, MoveStepsTask

# -----------------------------------------------------------------------------


class ActionCardTask(Task):
    def __call__(self, game_state: GameState) -> TaskResult:
        assert (chore := game_state.current_chore.action_card) is not None
        game_data = GAME_DATA[game_state.version]
        BACKEND_GAME_DATA = game_data.backend_game_data
        game_state.chore.action_card.pop(0)
        card = chore.card
        group = chore.group
        info = BACKEND_GAME_DATA.action_cards[group][card]
        player = game_state.logic.current_player

        if info.keep:
            game_state.logic.action[group][card].owner = player
            game_state, task = mod_release(game_state)
            return game_state, task

        game_state.logic.action_card[group].append(card)
        original_space = game_state.logic.player[game_state.logic.current_player].at

        if (amount := info.collect) is not None:
            game_state = mod_pay(game_state, None, player, amount)
            game_state, task = mod_release(game_state)
            return game_state, task

        if (amount := info.pay) is not None:
            prepare_pay_prompt(game_state, player)
            chore = PayChore(amount=amount, player=player, receiver=None)
            game_state.chore.pay.append(chore)
            game_state, task = mod_release(game_state)
            return game_state, task

        if (destination := info.move) is not None:
            game_state = MoveToSpaceTask.prepare(game_state)
            task = MoveToSpaceTask(destination=destination, player=player)
            return game_state, task

        if card == "#VT":
            game_state.chore.goto_jail.append(GotoJailChore(player=player))
            game_state, task = mod_release(game_state)
            return game_state, task

        if (card in ["#TTSD", "#SCN"]) and info.values is not None:
            bds_state = game_state.logic.bds
            house = int(info.values["$house"])
            hotel = int(info.values["$hotel"])
            n_houses = sum(
                bds_state[b].level
                for b in game_state.logic.bds
                if bds_state[b].level in range(1, 5) and bds_state[b].owner == player
            )

            n_hotels = sum(
                1
                for b in game_state.logic.bds
                if bds_state[b].level == 5 and bds_state[b].owner == player
            )

            amount = house * n_houses + hotel * n_hotels
            if amount > 0:
                prepare_pay_prompt(game_state, player)
                chore = PayChore(amount=amount, player=player, receiver=None)
                game_state.chore.pay.append(chore)

            game_state, task = mod_release(game_state)
            return game_state, task

        if card == "#R":
            game_state.logic.rent_multiplier = 2

            def check_last_space(space: str):
                return any(
                    space == b or space == b + "A"
                    for b in BACKEND_GAME_DATA.bds_group["R"].bds
                )

            game_state = MoveNearestTask.prepare(game_state)
            task = MoveNearestTask.create(
                original_space=original_space,
                player=game_state.logic.current_player,
                check_last_space=check_last_space,
            )
            return game_state, task

        if card == "#DL3B":
            game_state = MoveStepsTask.prepare(game_state)
            task = MoveStepsTask.from_steps(
                player=player, steps=3, change_track=False, reversed=True
            )
            return game_state, task

        if card == "#SNTC":
            game_state = MoveStepsTask.prepare(game_state)
            task = MoveStepsTask.from_steps(
                player=player, steps=3, change_track=False, reversed=False
            )
            return game_state, task

        if card == "#U" and info.values is not None:
            game_state.logic.u_multiplier = int(info.values["times"])

            def check_last_space(space: str):
                return space in BACKEND_GAME_DATA.bds_group["U"].bds

            game_state = MoveNearestTask.prepare(game_state)
            task = MoveNearestTask.create(
                original_space=original_space,
                player=player,
                check_last_space=check_last_space,
            )
            return game_state, task

        if card == "#KTNH" and info.values is not None:
            players = game_state.logic.player
            other_players = [p for p in players if players[p].alive and p != player]
            for p in other_players:
                chore = PayChore(
                    amount=int(info.values["$price"]), player=p, receiver=player
                )
                game_state.chore.pay.append(chore)
            game_state, task = mod_release(game_state)
            return game_state, task

        if card == "#DBLGD" and info.values is not None:
            players = game_state.logic.player
            other_players = [p for p in players if players[p].alive and p != player]
            new_chore = PayChore(
                amount=int(info.values["$price"]) * len(other_players),
                player=player,
                receiver=None,
            )
            game_state.chore.pay.append(new_chore)

        game_state, task = mod_release(game_state)
        return game_state, task


# -----------------------------------------------------------------------------


class TwoDiceRentUTask(Task):
    dice_1: str | None = None
    dice_2: str | None = None

    def __call__(self, game_state: GameState) -> TaskResult:
        assert (chore := game_state.current_chore.two_dice_rent_u) is not None
        assert (multiplier := game_state.logic.u_multiplier) is not None
        game_state.chore.two_dice_rent_u.pop(0)
        import random

        bds = chore.bds
        player = chore.player
        dice_1 = self.dice_1 or str(random.randint(1, 6))
        dice_2 = self.dice_2 or str(random.randint(1, 6))
        game_state.effect.dice_1 = str(dice_1)
        game_state.effect.dice_2 = str(dice_2)
        amount = (int(dice_1) + int(dice_2)) * multiplier
        owner = game_state.logic.bds[bds].owner
        prepare_pay_prompt(game_state, player)
        new_chore = PayChore(amount=amount, player=player, receiver=owner)
        game_state.chore.pay.append(new_chore)
        game_state, task = mod_release(game_state)
        return game_state, task


# -----------------------------------------------------------------------------


class UseActionCardTask(Task):
    group: str
    card: str

    def __call__(self, game_state: GameState) -> TaskResult:
        card = self.card
        player = game_state.logic.action[self.group][card].owner
        assert player is not None

        game_state.logic.action_card[self.group].append(card)

        task = None
        if card == "TDRT":
            assert (chore := game_state.current_chore.jail) is not None
            game_state.chore.jail.remove(chore)
            game_state = mod_get_outof_jail(game_state, player)
            game_state = prepare_roll_dice_prompt(game_state)
            next_chore = RollDiceChore()
            game_state.chore.roll_dice.append(next_chore)
            game_state, task = mod_release(game_state)
        return game_state, task


# -----------------------------------------------------------------------------
