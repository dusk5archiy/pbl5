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
export interface BuyPropertyRequest {
  game_state: GameState;
  property_id: string;
  buy: boolean;
}

export interface BuyPropertyResponse {
  new_game_state: GameState;
}

export async function buyProperty(request: BuyPropertyRequest): Promise<BuyPropertyResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/buy_property`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`Failed to buy property: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error buying property:', error);
    throw error;
  }
}

export interface PayRentRequest {
  game_state: GameState;
  property_id: string;
}

export interface PayRentResponse {
  new_game_state: GameState;
}

export async function payRent(request: PayRentRequest): Promise<PayRentResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/pay_rent`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`Failed to pay rent: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error paying rent:', error);
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

export interface PropertyActionRequest {
  game_state: GameState;
  property_id: string;
}

export interface PropertyActionResponse {
  new_game_state: GameState;
}

export async function upgradeProperty(request: PropertyActionRequest): Promise<PropertyActionResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/upgrade_property`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`Failed to upgrade property: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error upgrading property:', error);
    throw error;
  }
}

export async function downgradeProperty(request: PropertyActionRequest): Promise<PropertyActionResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/downgrade_property`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`Failed to downgrade property: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error downgrading property:', error);
    throw error;
  }
}

export async function mortgageProperty(request: PropertyActionRequest): Promise<PropertyActionResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/mortgage_property`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`Failed to mortgage property: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error mortgaging property:', error);
    throw error;
  }
}

export async function unmortgageProperty(request: PropertyActionRequest): Promise<PropertyActionResponse> {
  try {
    const response = await fetch(`${API_BASE_URL}/unmortgage_property`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    if (!response.ok) {
      throw new Error(`Failed to unmortgage property: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Error unmortgaging property:', error);
    throw error;
  }
}