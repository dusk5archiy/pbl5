from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from game_data_manager import (
    GAME_DATA,
)
from logic import (
    AuctionBdsTask,
    BuyTask,
    RollDiceTask,
    EndTurnTask,
    MortgageTask,
    PayTask,
    ReceiveMortgageTask,
    UnmortgageTask,
    UpgradeTask,
    DowngradeTask,
    JailTask,
)
from model.game_data import FrontendGameData
from model.game_state import GameState
from logic import generate_states
from task.action_card import ActionCardTask, TwoDiceRentUTask, UseActionCardTask
from task.dice import DiceCTask, DiceXbTask, TripleDiceTask
from model.game_state import (
    GameEffectState,
    GameLogicState,
    GameUiState,
    LogicStateBDS,
    LogicStateBuild,
    LogicStatePlayer,
    LogicStateAction,
)

from model.chore import EndTurnChore, TradeCard
from task.trade import StartTradeTask, TradeTask

# -----------------------------------------------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Replace `*` with the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------


@app.get("/handshake")
async def handshake():
    return None


# -----------------------------------------------------------------------------


class StateRequest(BaseModel):
    game_state: GameState


class StateResponse(BaseModel):
    game_states: list[GameState]


class RollDiceRequest(BaseModel):
    game_state: GameState
    dice_1: str | None = None
    dice_2: str | None = None


@app.post("/roll_dice", response_model=StateResponse)
async def roll_dice(request: RollDiceRequest) -> StateResponse:
    game_state = request.game_state
    task = RollDiceTask(dice_1=request.dice_1, dice_2=request.dice_2)
    return StateResponse(game_states=list(generate_states(game_state, task)))


@app.post("/end_turn", response_model=StateResponse)
async def end_turn(request: StateRequest) -> StateResponse:
    game_state = request.game_state
    task = EndTurnTask()
    return StateResponse(game_states=list(generate_states(game_state, task)))


# -----------------------------------------------------------------------------


class NumRequest(BaseModel):
    game_state: GameState
    response: int


class DiceNumRequest(NumRequest):
    dice_1: str | None = None
    dice_2: str | None = None


@app.post("/buy", response_model=StateResponse)
async def buy(request: NumRequest) -> StateResponse:
    game_state = request.game_state
    task = BuyTask(response=request.response)
    return StateResponse(game_states=list(generate_states(game_state, task)))


# -----------------------------------------------------------------------------


class AuctionRequest(BaseModel):
    game_state: GameState
    amount: int


@app.post("/auction", response_model=StateResponse)
async def auction(request: AuctionRequest) -> StateResponse:
    game_state = request.game_state
    task = AuctionBdsTask(amount=request.amount)
    return StateResponse(game_states=list(generate_states(game_state, task)))


# -----------------------------------------------------------------------------


class BdsRequest(BaseModel):
    game_state: GameState
    bds: str


@app.post("/upgrade_bds", response_model=StateResponse)
async def upgrade_bds(request: BdsRequest) -> StateResponse:
    game_state = request.game_state
    task = UpgradeTask(bds=request.bds)
    return StateResponse(game_states=list(generate_states(game_state, task)))


@app.post("/downgrade_bds", response_model=StateResponse)
async def downgrade_bds(request: BdsRequest) -> StateResponse:
    game_state = request.game_state
    task = DowngradeTask(bds=request.bds)
    return StateResponse(game_states=list(generate_states(game_state, task)))


@app.post("/mortgage_bds", response_model=StateResponse)
async def mortgage_bds(request: BdsRequest) -> StateResponse:
    game_state = request.game_state
    task = MortgageTask(bds=request.bds)
    return StateResponse(game_states=list(generate_states(game_state, task)))


@app.post("/unmortgage_bds", response_model=StateResponse)
async def unmortgage_bds(request: BdsRequest) -> StateResponse:
    game_state = request.game_state
    task = UnmortgageTask(bds=request.bds)
    return StateResponse(game_states=list(generate_states(game_state, task)))


# -----------------------------------------------------------------------------


@app.post("/pay", response_model=StateResponse)
async def pay(request: NumRequest) -> StateResponse:
    game_state = request.game_state
    task = PayTask(response=request.response)
    return StateResponse(game_states=list(generate_states(game_state, task)))


# -----------------------------------------------------------------------------


@app.post("/receive_mortgage", response_model=StateResponse)
async def receive_mortgage(request: NumRequest) -> StateResponse:
    game_state = request.game_state
    task = ReceiveMortgageTask(response=request.response)
    return StateResponse(game_states=list(generate_states(game_state, task)))


# -----------------------------------------------------------------------------


@app.post("/jail", response_model=StateResponse)
async def jail(request: DiceNumRequest) -> StateResponse:
    game_state = request.game_state
    task = JailTask(
        response=request.response, dice_1=request.dice_1, dice_2=request.dice_2
    )
    return StateResponse(game_states=list(generate_states(game_state, task)))


# -----------------------------------------------------------------------------


@app.post("/dice_c", response_model=StateResponse)
async def dice_c(request: StateRequest) -> StateResponse:
    game_state = request.game_state
    task = DiceCTask()
    return StateResponse(game_states=list(generate_states(game_state, task)))


@app.post("/dice_xb", response_model=StateResponse)
async def dice_xb(request: StateRequest) -> StateResponse:
    game_state = request.game_state
    task = DiceXbTask()
    return StateResponse(game_states=list(generate_states(game_state, task)))


class DestinationRequest(BaseModel):
    game_state: GameState
    destination: str


@app.post("/triple_dice", response_model=StateResponse)
async def triple_dice(request: DestinationRequest) -> StateResponse:
    game_state = request.game_state
    task = TripleDiceTask(destination=request.destination)
    return StateResponse(game_states=list(generate_states(game_state, task)))


@app.post("/action_card", response_model=StateResponse)
async def action_card(request: StateRequest) -> StateResponse:
    game_state = request.game_state
    task = ActionCardTask()
    return StateResponse(game_states=list(generate_states(game_state, task)))


@app.post("/two_dice_rent_u", response_model=StateResponse)
async def two_dice_rent_u(request: RollDiceRequest) -> StateResponse:
    game_state = request.game_state
    task = TwoDiceRentUTask(dice_1=request.dice_1, dice_2=request.dice_2)
    return StateResponse(game_states=list(generate_states(game_state, task)))


# -----------------------------------------------------------------------------


class UseActionCardRequest(BaseModel):
    game_state: GameState
    group: str
    card: str


@app.post("/use_action_card", response_model=StateResponse)
async def use_action_card(request: UseActionCardRequest) -> StateResponse:
    game_state = request.game_state
    task = UseActionCardTask(group=request.group, card=request.card)
    return StateResponse(game_states=list(generate_states(game_state, task)))


# -----------------------------------------------------------------------------


@app.post("/start_trade", response_model=StateResponse)
async def start_trade(request: StateRequest) -> StateResponse:
    game_state = request.game_state
    task = StartTradeTask()
    return StateResponse(game_states=list(generate_states(game_state, task)))


class TradeRequest(BaseModel):
    game_state: GameState
    player_2: str | None = None
    bds: str | None = None
    card: TradeCard | None = None
    money_1: int | None = None
    money_2: int | None = None
    response: int | None = None


@app.post("/trade", response_model=StateResponse)
async def trade(request: TradeRequest) -> StateResponse:
    game_state = request.game_state
    task = TradeTask(
        player_2=request.player_2,
        bds=request.bds,
        card=request.card,
        money_1=request.money_1,
        money_2=request.money_2,
        response=request.response,
    )
    return StateResponse(game_states=list(generate_states(game_state, task)))


# -----------------------------------------------------------------------------


class GameStateRequest(BaseModel):
    players: list[str]
    version: str = "1"


class GameStateResponse(BaseModel):
    game_state: GameState
    game_data: FrontendGameData


@app.post("/initial_game_state", response_model=GameStateResponse)
async def initial_game_state(request: GameStateRequest) -> GameStateResponse:
    import random

    game_data = GAME_DATA[request.version]
    FRONTEND_GAME_DATA, BACKEND_GAME_DATA = (
        game_data.frontend_game_data,
        game_data.backend_game_data,
    )

    players = request.players
    random.shuffle(players)
    backend_logic = BACKEND_GAME_DATA.logic

    action_card_dict = {group: [] for group in BACKEND_GAME_DATA.action_cards}

    for group, d in BACKEND_GAME_DATA.action_cards.items():
        for card_id, info in d.items():
            action_card_dict[group].extend([card_id for _ in range(info.copies)])

        random.shuffle(action_card_dict[group])

    backend_action_cards = BACKEND_GAME_DATA.action_cards
    player = players[0]
    logic = GameLogicState(
        bds={bds_id: LogicStateBDS() for bds_id in FRONTEND_GAME_DATA.bds.keys()},
        player={
            player: LogicStatePlayer(
                budget=backend_logic.init_budget, at=backend_logic.start_at
            )
            for player in players
        },
        current_player=player,
        player_order=players,
        build=LogicStateBuild(
            house=backend_logic.init_house,
            hotel=backend_logic.init_hotel,
            skyscraper=backend_logic.init_skyscraper,
        ),
        action_card=action_card_dict,
        action={
            group: {
                card_id: LogicStateAction()
                for card_id in backend_action_cards[group]
                if backend_action_cards[group][card_id].keep
            }
            for group in backend_action_cards
        },
    )
    ui = GameUiState.new(logic)
    game_state = GameState(
        version=request.version,
        logic=logic,
        ui=ui,
        effect=GameEffectState(
            board=FRONTEND_GAME_DATA.space[backend_logic.start_at].board,
        ),
    )
    game_state.current_chore.end_turn = EndTurnChore(next_player=False, player=player)
    gen = generate_states(game_state, EndTurnTask())
    game_state = next(gen)
    return GameStateResponse(game_state=game_state, game_data=FRONTEND_GAME_DATA)


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    import yaml
    from colorama import Fore, init

    init()

    with open("../config.yml", "r") as f:
        config = yaml.safe_load(f)

    print(Fore.CYAN + "[-- INFO --] Configurations: ")
    print(config)

    uvicorn.run(app, port=config["back"]["port"])
