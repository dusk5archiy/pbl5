import { RefObject } from 'react';
import { GameData, GameState } from "@/app/model/game";
import {
  AuctionRequest,
  BdsRequest as BdsRequest,
  DestinationRequest,
  NumRequest,
  RollDiceRequest,
  TradeRequest,
  UseActionCardRequest,
  DiceNumRequest,
} from "@/app/screen/game-screen/props";

// ----------------------------------------------------------------------------

export interface IGameDataStateProps {
  gameState: GameState;
  gameData: GameData;
}

export interface IPropertySelectorsProps {
  selectedBoard: number;
  selectedTrack: number;
  selectedGroup: string;
  selectedBds: string;
  setSelectedBoard: (_: number) => void;
  setSelectedTrack: (_: number) => void;
  setSelectedGroup: (_: string) => void;
  setSelectedBds: (_: string) => void;
  focusBds: (_: string) => void;
}

export interface IActionCardSelectorsProps {
  selectedActionGroup: string;
  selectedActionCard: string;
  setSelectedActionGroup: (_: string) => void;
  setSelectedActionCard: (_: string) => void;
}

export interface IApiProps {
  buyFunc: (_: NumRequest) => void;
  tripleDiceFunc: (_: DestinationRequest) => void;
  auctionFunc: (_: AuctionRequest) => void;
  payFunc: (_: NumRequest) => void;
  receiveMortgageFunc: (_: NumRequest) => void;
  tradeFunc: (_: TradeRequest) => void;
  rollDiceFunc: (_: RollDiceRequest) => void;
  endTurnFunc: () => void;
  jailFunc: (_: DiceNumRequest) => void;
  twoDiceRentUFunc: (_: RollDiceRequest) => void;
  diceCFunc: () => void;
  diceXbFunc: () => void;
  actionCardFunc: () => void;
  upgradeBdsFunc: (_: BdsRequest) => void;
  downgradeBdsFunc: (_: BdsRequest) => void;
  mortgageBdsFunc: (_: BdsRequest) => void;
  unmortgageBdsFunc: (_: BdsRequest) => void;
  useActionCardFunc: (_: UseActionCardRequest) => void;
  startTradeFunc: () => void;
}

// ----------------------------------------------------------------------------

export interface IDice {
  dice_1?: string;
  dice_2?: string;
}

export interface IDiceDetectionResult {
  scores: number[];
  bboxes: number[][];
}
export interface IDiceDetectionProps {
  selectedCamera: string;
  videoRef: RefObject<HTMLVideoElement | null>;
  stream: MediaStream | null;
  setStream: (_: MediaStream) => void;
  diceDetectionResult: IDiceDetectionResult | null;
  setDiceDetectionResult: (_: IDiceDetectionResult | null) => void;
  sendFrame: () => void;
  encodedImage: string | null;
  setEncodedImage: (_: string | null) => void;
  isAutoCapturing: boolean;
  setIsAutoCapturing: (_: boolean) => void;
}

// ----------------------------------------------------------------------------

export interface IGameSettingsProps {
  diceDetection: boolean;
  selectedCamera: string;
}

// ----------------------------------------------------------------------------

export interface ISendDataProps {
  sendRollDice: () => void;
}

// ----------------------------------------------------------------------------

export interface GameBoardProps extends
  IPropertySelectorsProps,
  IGameDataStateProps,
  IApiProps,
  IActionCardSelectorsProps,
  IDiceDetectionProps, IGameSettingsProps,
  ISendDataProps {
  getBoardNum: number;
  bdsShown: number
  setBdsShown: (_: number) => void;
  propertyTab: string;
  setPropertyTab: (_: string) => void;
  guest?: string;
  boardShown: boolean;
}

// ----------------------------------------------------------------------------
