from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import VERSION, BaseModel
import asyncio
import json
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


class RollDiceRequest(BaseModel):
    game_state: GameState
    dice_1: str | None = None
    dice_2: str | None = None


# -----------------------------------------------------------------------------


class NumRequest(BaseModel):
    game_state: GameState
    response: int


class DiceNumRequest(NumRequest):
    dice_1: str | None = None
    dice_2: str | None = None


# -----------------------------------------------------------------------------


class AuctionRequest(BaseModel):
    game_state: GameState
    amount: int


# -----------------------------------------------------------------------------


class BdsRequest(BaseModel):
    game_state: GameState
    bds: str


# -----------------------------------------------------------------------------


class DestinationRequest(BaseModel):
    game_state: GameState
    destination: str


class UseActionCardRequest(BaseModel):
    game_state: GameState
    group: str
    card: str


# -----------------------------------------------------------------------------


class TradeRequest(BaseModel):
    game_state: GameState
    player_2: str | None = None
    bds: str | None = None
    card: TradeCard | None = None
    money_1: int | None = None
    money_2: int | None = None
    response: int | None = None


# -----------------------------------------------------------------------------


class GameStateRequest(BaseModel):
    players: list[str]
    version: str = "1"


class GameStateResponse(BaseModel):
    game_state: GameState
    game_data: FrontendGameData


@app.post("/initial_game_state", response_model=GameStateResponse)
async def initial_game_state(request: GameStateRequest) -> GameStateResponse:
    global game_state_server
    import random

    version = request.version
    game_data = GAME_DATA[version]
    FRONTEND_GAME_DATA, BACKEND_GAME_DATA = (
        game_data.frontend_game_data,
        game_data.backend_game_data,
    )

    if game_state_server is not None:
        return GameStateResponse(game_state=game_state_server, game_data=FRONTEND_GAME_DATA)

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

    logic_budget = {player: backend_logic.init_budget for player in players}

    if BACKEND_GAME_DATA.logic.use_pool:
        logic_budget = logic_budget | {"pool": 0}

    logic = GameLogicState(
        bds={bds_id: LogicStateBDS() for bds_id in FRONTEND_GAME_DATA.bds.keys()},
        player={
            player: LogicStatePlayer(at=backend_logic.start_at) for player in players
        },
        budget=logic_budget,
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
    game_state_server = game_state
    return GameStateResponse(game_state=game_state, game_data=FRONTEND_GAME_DATA)


# -----------------------------------------------------------------------------
list_connection = []
game_state_server = None
@app.websocket("/ws/game_states")
async def websocket_game_states(websocket: WebSocket):
    global game_state_server
    await websocket.accept()
    list_connection.append(websocket)
    try:
        while True:
            try:
                data = await websocket.receive_text()
                msg = json.loads(data)
                action = msg["action"]
                params = msg.get("params", {})
                params["game_state"] = msg["game_state"]

                task = None
                game_state = None

                if action == "roll_dice":
                    request = RollDiceRequest(**params)
                    game_state = request.game_state
                    task = RollDiceTask(dice_1=request.dice_1, dice_2=request.dice_2)

                elif action == "end_turn":
                    request = StateRequest(**params)
                    game_state = request.game_state
                    task = EndTurnTask()

                elif action == "buy":
                    request = NumRequest(**params)
                    game_state = request.game_state
                    task = BuyTask(response=request.response)

                elif action == "auction":
                    request = AuctionRequest(**params)
                    game_state = request.game_state
                    task = AuctionBdsTask(amount=request.amount)

                elif action == "upgrade_bds":
                    request = BdsRequest(**params)
                    game_state = request.game_state
                    task = UpgradeTask(bds=request.bds)

                elif action == "downgrade_bds":
                    request = BdsRequest(**params)
                    game_state = request.game_state
                    task = DowngradeTask(bds=request.bds)

                elif action == "mortgage_bds":
                    request = BdsRequest(**params)
                    game_state = request.game_state
                    task = MortgageTask(bds=request.bds)

                elif action == "unmortgage_bds":
                    request = BdsRequest(**params)
                    game_state = request.game_state
                    task = UnmortgageTask(bds=request.bds)

                elif action == "pay":
                    request = NumRequest(**params)
                    game_state = request.game_state
                    task = PayTask(response=request.response)

                elif action == "receive_mortgage":
                    request = NumRequest(**params)
                    game_state = request.game_state
                    task = ReceiveMortgageTask(response=request.response)

                elif action == "jail":
                    request = DiceNumRequest(**params)
                    game_state = request.game_state
                    task = JailTask(
                        response=request.response,
                        dice_1=request.dice_1,
                        dice_2=request.dice_2,
                    )

                elif action == "dice_c":
                    request = StateRequest(**params)
                    game_state = request.game_state
                    task = DiceCTask()

                elif action == "dice_xb":
                    request = StateRequest(**params)
                    game_state = request.game_state
                    task = DiceXbTask()

                elif action == "triple_dice":
                    request = DestinationRequest(**params)
                    game_state = request.game_state
                    task = TripleDiceTask(destination=request.destination)

                elif action == "action_card":
                    request = StateRequest(**params)
                    game_state = request.game_state
                    task = ActionCardTask()

                elif action == "two_dice_rent_u":
                    request = RollDiceRequest(**params)
                    game_state = request.game_state
                    task = TwoDiceRentUTask(
                        dice_1=request.dice_1, dice_2=request.dice_2
                    )

                elif action == "use_action_card":
                    request = UseActionCardRequest(**params)
                    game_state = request.game_state
                    task = UseActionCardTask(group=request.group, card=request.card)

                elif action == "start_trade":
                    request = StateRequest(**params)
                    game_state = request.game_state
                    task = StartTradeTask()

                elif action == "trade":
                    request = TradeRequest(**params)
                    game_state = request.game_state
                    task = TradeTask(**params)

                if task is not None and game_state is not None:
                    for state in generate_states(game_state, task):
                        game_state_server = state
                        for connection in list_connection:
                            await connection.send_text(state.model_dump_json())
                        delay = state.effect.wait_ms
                        await asyncio.sleep(delay / 1000.0)
            except Exception as e:
                import traceback

                traceback.print_exc()
                print(f"WebSocket processing error: {e}")
                break
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        list_connection.remove(websocket)
        if len(list_connection) == 0:
            game_state_server = None
            
        print("Players left:", len(list(list_connection)))
        await websocket.close()


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    import yaml
    from colorama import Fore, init

    init()

    with open("../config/config.yml", "r") as f:
        config = yaml.safe_load(f)

    print(Fore.CYAN + "[-- INFO --] Configurations: ")
    print(config)

    uvicorn.run(app, host="0.0.0.0", port=config["back"]["port"])
