import {
  AuctionRequest,
  DestinationRequest,
  GameScreenProps,
  BdsRequest,
  TradeRequest,
  UseActionCardRequest,
  NumRequest,
  DiceNumRequest,
  RollDiceRequest
} from "./props";

// ----------------------------------------------------------------------------

export async function getFunction(props: GameScreenProps, at: string, request: Object = {}, ws: WebSocket) {
  const { gameState, onError, updating, setUpdating } = props;
  return async () => {
    if (updating) {
      return;
    }
    setUpdating(true);
    try {
      const message = {
        action: at,
        game_state: gameState,
        params: request
      };
      ws.send(JSON.stringify(message));
    } catch {
      onError();
    }
  };
}

// ----------------------------------------------------------------------------

export function getNormalFunction(props: GameScreenProps, at: string, ws: WebSocket) {
  return async () => {
    const func = await getFunction(props, at, {}, ws);
    await func();
  };
}
// ----------------------------------------------------------------------------

export function getRollDiceFunction(props: GameScreenProps, at: string, ws: WebSocket) {
  return async (request: RollDiceRequest) => {
    const func = await getFunction(props, at, request, ws);
    await func();
  };
}
export function getNumFunction(props: GameScreenProps, at: string, ws: WebSocket) {
  return async (request: NumRequest) => {
    const func = await getFunction(props, at, request, ws);
    await func();
  };
}

export function getDiceNumFunction(props: GameScreenProps, at: string, ws: WebSocket) {
  return async (request: DiceNumRequest) => {
    const func = await getFunction(props, at, request, ws);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getAuctionFunction(props: GameScreenProps, at: string, ws: WebSocket) {
  return async (request: AuctionRequest) => {
    const func = await getFunction(props, at, request, ws);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getBdsFunction(props: GameScreenProps, at: string, ws: WebSocket) {
  return async (request: BdsRequest) => {
    const func = await getFunction(props, at, request, ws);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getDestinationFunction(props: GameScreenProps, at: string, ws: WebSocket) {
  return async (request: DestinationRequest) => {
    const func = await getFunction(props, at, request, ws);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getUseActionCardFunction(props: GameScreenProps, at: string, ws: WebSocket) {
  return async (request: UseActionCardRequest) => {
    const func = await getFunction(props, at, request, ws);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getTradeFunction(props: GameScreenProps, at: string, ws: WebSocket) {
  return async (request: TradeRequest) => {
    const func = await getFunction(props, at, request, ws);
    await func();
  };
}

// ----------------------------------------------------------------------------

