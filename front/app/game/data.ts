import { GameData, GameDataResponse } from './model';

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