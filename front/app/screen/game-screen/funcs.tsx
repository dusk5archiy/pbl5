import { GameState } from "@/app/model/game";
import { callApi } from '@/app/utils/api';
import {
  AuctionRequest,
  DestinationRequest,
  GameScreenProps,
  MortgageBdsRequest,
  TradeRequest,
  UseActionCardRequest,
  NumRequest,
  DiceNumRequest,
  RollDiceRequest
} from "./props";

// ----------------------------------------------------------------------------

export function getUpdateGameStateFunction(
  setGameState: (gameState: GameState) => void,
) {
  return async (game_states: GameState[]) => {
    let idx = 0;
    const len = game_states.length;
    const iter = () => {
      const game_state = game_states[idx];
      setGameState(game_state);
      const delay = game_states[idx].effect.wait_ms;
      idx++;
      if (idx < len) {
        setTimeout(iter, delay);
      }
    }

    if (game_states.length > 0) {
      iter();
    }
  };
}

// ----------------------------------------------------------------------------

export async function getFunction(props: GameScreenProps, at: string, request: Object = {}) {
  const { gameState, onError, setGameState, updating, setUpdating } = props;
  const updateGameState = getUpdateGameStateFunction(setGameState);
  return async () => {
    if (updating) {
      return;
    }
    setUpdating(true);
    try {
      const data = await callApi(at, { game_state: gameState, ...request });
      const game_states = data.game_states as GameState[];
      updateGameState(game_states);
    } catch {
      onError();
    }
    setUpdating(false);
  };
}

// ----------------------------------------------------------------------------

export function getNormalFunction(props: GameScreenProps, at: string) {
  return async () => {
    const func = await getFunction(props, at, {});
    await func();
  };
}
// ----------------------------------------------------------------------------

export function getRollDiceFunction(props: GameScreenProps, at: string) {
  return async (request: RollDiceRequest) => {
    const func = await getFunction(props, at, request);
    await func();
  };
}
export function getNumFunction(props: GameScreenProps, at: string) {
  return async (request: NumRequest) => {
    const func = await getFunction(props, at, request);
    await func();
  };
}

export function getDiceNumFunction(props: GameScreenProps, at: string) {
  return async (request: DiceNumRequest) => {
    const func = await getFunction(props, at, request);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getAuctionFunction(props: GameScreenProps, at: string) {
  return async (request: AuctionRequest) => {
    const func = await getFunction(props, at, request);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getBdsFunction(props: GameScreenProps, at: string) {
  return async (request: MortgageBdsRequest) => {
    const func = await getFunction(props, at, request);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getDestinationFunction(props: GameScreenProps, at: string) {
  return async (request: DestinationRequest) => {
    const func = await getFunction(props, at, request);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getUseActionCardFunction(props: GameScreenProps, at: string) {
  return async (request: UseActionCardRequest) => {
    const func = await getFunction(props, at, request);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getTradeFunction(props: GameScreenProps, at: string) {
  return async (request: TradeRequest) => {
    const func = await getFunction(props, at, request);
    await func();
  };
}

// ----------------------------------------------------------------------------

