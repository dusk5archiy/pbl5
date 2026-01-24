from game_logic import calculate_player_total, BDAU_SALARY
from game_model import GameState, PendingAction
from typing import Callable

SpaceEffect = Callable[[GameState, str], None]


# Space effects configuration
# Effects that trigger when touching a space (passing through or landing)
def bdau_effect(state: GameState, player_id: str) -> None:
    """Add salary when passing through or landing on BDAU"""
    state.players[player_id].budget += BDAU_SALARY
    state.players[player_id].total = calculate_player_total(state, player_id)


def go_to_jail_effect(state: GameState, player_id: str) -> None:
    """Send player to jail - mark as in jail (position updated separately)"""
    state.players[player_id].in_jail = True
    state.players[player_id].jail_turns = 0
    # Reset double roll stack when going to jail
    state.double_roll_stack = 0


def income_tax_effect(state: GameState, player_id: str) -> None:
    """Income tax - 10% of total value, max 200k"""
    player_total = calculate_player_total(state, player_id)
    tax = min(int(player_total * 0.1), 200)
    state.pending_actions.append(
        PendingAction(type="pay_tax", data={"tax_type": "income", "amount": tax})
    )


def luxury_tax_effect(state: GameState, _: str) -> None:
    """Luxury tax - flat 75k"""
    state.pending_actions.append(
        PendingAction(type="pay_tax", data={"tax_type": "luxury", "amount": 75})
    )


EFFECTS_ON_TOUCH: dict[str, SpaceEffect] = {"BDAU": bdau_effect}

# Effects that trigger only when landing on a space
EFFECTS_ON_LAND: dict[str, SpaceEffect] = {
    "VT": go_to_jail_effect,  # VT is Go to Jail space
    "TTN": income_tax_effect,  # TTN is Income Tax
    "TDB": luxury_tax_effect,  # TDB is Luxury Tax
}
