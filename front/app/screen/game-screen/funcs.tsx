import { GameState } from "@/app/model/game";
import { getApi } from '@/app/utils/api';
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

export function getFunction(props: GameScreenProps, at: string, request: Object = {}) {
  const { gameState, onError, setGameState, updating, setUpdating } = props;
  const updateGameState = getUpdateGameStateFunction(setGameState);
  const api = getApi(onError, at, { game_state: gameState, ...request });
  return async () => {
    if (updating) {
      return;
    }
    setUpdating(true);
    const data = await api();
    setUpdating(false);
    if (data === undefined) return;
    const game_states = data.game_states as GameState[];
    updateGameState(game_states);
  };
}

// ----------------------------------------------------------------------------

export function getRollDiceFunction(props: GameScreenProps, at: string) {
  return async (request: RollDiceRequest) => {
    const func = getFunction(props, at, request);
    await func();
  };
}
export function getNumFunction(props: GameScreenProps, at: string) {
  return async (request: NumRequest) => {
    const func = getFunction(props, at, request);
    await func();
  };
}

export function getDiceNumFunction(props: GameScreenProps, at: string) {
  return async (request: DiceNumRequest) => {
    const func = getFunction(props, at, request);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getAuctionFunction(props: GameScreenProps, at: string) {
  return async (request: AuctionRequest) => {
    const func = getFunction(props, at, request);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getBdsFunction(props: GameScreenProps, at: string) {
  return async (request: MortgageBdsRequest) => {
    const func = getFunction(props, at, request);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getDestinationFunction(props: GameScreenProps, at: string) {
  return async (request: DestinationRequest) => {
    const func = getFunction(props, at, request);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getUseActionCardFunction(props: GameScreenProps, at: string) {
  return async (request: UseActionCardRequest) => {
    const func = getFunction(props, at, request);
    await func();
  };
}

// ----------------------------------------------------------------------------

export function getTradeFunction(props: GameScreenProps, at: string) {
  return async (request: TradeRequest) => {
    const func = getFunction(props, at, request);
    await func();
  };
}

// ----------------------------------------------------------------------------

