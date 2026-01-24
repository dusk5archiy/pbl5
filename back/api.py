from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from game_data import GAME_DATA
import mech.manage_bds as mech_manage_bds
import mech.bds as mech_bds
import mech.dice as mech_dice
import mech.init as mech_init
import mech.turn as mech_turn
import mech.tax as mech_tax
import mech.jail as mech_jail
import mech.data as mech_data

# -----------------------------------------------------------------------------

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------


@app.post("/init_game", response_model=mech_init.InitGameResponse)
async def init_game(request: mech_init.InitGameRequest):
    return mech_init.init_game(request)


# -----------------------------------------------------------------------------


@app.post("/move_with_dice", response_model=mech_dice.RollDiceResponse)
async def move_with_dice(request: mech_dice.RollDiceRequest):
    return mech_dice.move_with_dice(request)


# -----------------------------------------------------------------------------


@app.post("/next_turn", response_model=mech_turn.NextTurnResponse)
async def next_turn(request: mech_turn.NextTurnRequest):
    return mech_turn.next_turn(request)


# -----------------------------------------------------------------------------


@app.post("/upgrade_property", response_model=mech_manage_bds.PropertyActionResponse)
async def upgrade_property(request: mech_manage_bds.PropertyActionRequest):
    return mech_manage_bds.upgrade_property(request)


# -----------------------------------------------------------------------------


@app.post("/downgrade_property", response_model=mech_manage_bds.PropertyActionResponse)
async def downgrade_property(request: mech_manage_bds.PropertyActionRequest):
    return mech_manage_bds.downgrade_property(request)


# -----------------------------------------------------------------------------


@app.post("/mortgage_property", response_model=mech_manage_bds.PropertyActionResponse)
async def mortgage_property(request: mech_manage_bds.PropertyActionRequest):
    return mech_manage_bds.mortgage_property(request)


# -----------------------------------------------------------------------------


@app.post("/unmortgage_property", response_model=mech_manage_bds.PropertyActionResponse)
async def unmortgage_property(request: mech_manage_bds.PropertyActionRequest):
    return mech_manage_bds.unmortgage_property(request)


# -----------------------------------------------------------------------------


@app.post("/buy_property", response_model=mech_bds.BuyPropertyResponse)
async def buy_property(
    request: mech_bds.BuyPropertyRequest,
) -> mech_bds.BuyPropertyResponse:
    return mech_bds.buy_property(request)


# -----------------------------------------------------------------------------


@app.post("/pay_rent", response_model=mech_bds.PayRentResponse)
async def pay_rent(request: mech_bds.PayRentRequest):
    return mech_bds.pay_rent(request)


# -----------------------------------------------------------------------------


@app.post("/pay_tax", response_model=mech_tax.PayTaxResponse)
async def pay_tax(request: mech_tax.PayTaxRequest):
    return mech_tax.pay_tax(request)


# -----------------------------------------------------------------------------


@app.post("/pay_jail_fine", response_model=mech_jail.PayJailFineResponse)
async def pay_jail_fine(
    request: mech_jail.PayJailFineRequest,
) -> mech_jail.PayJailFineResponse:
    return mech_jail.pay_jail_fine(request)


# -----------------------------------------------------------------------------


@app.get("/game_data", response_model=mech_data.GameDataResponse)
async def get_game_data():
    return mech_data.get_game_data()


# -----------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
