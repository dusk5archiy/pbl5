import { GameData, GameDataResponse, GameState } from './model';

const API_BASE_URL = 'http://localhost:8001';
let gameData: GameData | null = null;

export async function fetchGameData(): Promise<GameData> {
  if (gameData) {
    return gameData;
  }

  try {
    const response = await fetch(`${API_BASE_URL}/game_data`);
    if (!response.ok) {
      throw new Error(`Failed to fetch game data: ${response.statusText}`);
    }
    const data: GameDataResponse = await response.json();
    gameData = data.game_data;
    return gameData;
  } catch (error) {
    console.error('Error fetching game data:', error);
    throw error;
  }
}

export interface MoveWithDiceRequest {
  game_state: GameState;
  dice1: number;
  dice2: number;
}

export interface MoveWithDiceResponse {
  intermediate_states: GameState[];
}

export async function moveWithDice(request: MoveWithDiceRequest): Promise<MoveWithDiceResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/move_with_dice`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`Failed to move with dice: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error moving with dice:', error);
    throw error;
  }
}

export interface NextTurnRequest {
  game_state: GameState;
}

export interface NextTurnResponse {
  new_game_state: GameState;
}

export async function nextTurn(request: NextTurnRequest): Promise<NextTurnResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/next_turn`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`Failed to move to next turn: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error moving to next turn:', error);
    throw error;
  }
}