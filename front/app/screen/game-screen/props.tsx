import { GameData, GameState } from "@/app/model/game"
import { TradeCard } from "@/app/model/chore";

// ----------------------------------------------------------------------------

export interface GameScreenProps {
  onBack: () => void;
  onError: (_?: any) => void;
  gameData: GameData;
  gameState: GameState;
  setGameState: (gameState: GameState) => void;
  updating: boolean;
  setUpdating: (_: boolean) => void;
  selectedCamera: string;
  diceDetection: boolean;
};

// ----------------------------------------------------------------------------

export interface RollDiceRequest {
  dice_1?: string;
  dice_2?: string;
}

export interface NumRequest {
  response: number
}

export interface DiceNumRequest extends NumRequest {
  dice_1?: string;
  dice_2?: string;
}

// ----------------------------------------------------------------------------

export interface AuctionRequest {
  amount: number
}

// ----------------------------------------------------------------------------

export interface BdsRequest {
  bds: string;
}

// ----------------------------------------------------------------------------

export interface DestinationRequest {
  destination: string;
}

// ----------------------------------------------------------------------------

export interface UseActionCardRequest {
  group: string;
  card: string;
}

// ----------------------------------------------------------------------------

export interface TradeRequest {
  player_2?: string;
  bds?: string;
  card?: TradeCard;
  money_1?: number;
  money_2?: number;
  response?: number
}

// ----------------------------------------------------------------------------
