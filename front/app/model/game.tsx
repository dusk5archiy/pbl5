import { Chore, CurrentChore } from "./chore";

// ----------------------------------------------------------------------------

export interface Space {
  orient: string;
  board: number;
  track: number;
  x: number;
  y: number;
  w: number;
  h: number;
}

// ----------------------------------------------------------------------------

export interface BDS {
  name: string;
  group: string;
  price: number;
  rent: number[];
  level_start: number;
  mortgage: number;
  upgrade?: number;
  downgrade?: number;
  unmortgage: number;
}

// ----------------------------------------------------------------------------

export interface TrackBorder {
  top_left: number;
  bottom_right: number;
}

// ----------------------------------------------------------------------------

export interface Action {
  name: string;
  group: string;
}

export interface ActionCard {
  name: string;
  content: string;
  foot: string;
}

// ----------------------------------------------------------------------------

export interface GameData {
  space: Record<string, Space>;
  space_id_list: Array<Array<string>>;
  board_size: Array<number>;
  pallete: Record<string, string>;
  bds: Record<string, BDS>;
  special_space: Record<string, Space>;
  track_border: Array<Array<TrackBorder>>
  action: Record<string, Action>;
  action_label: Record<string, string>;
  action_special_label: Record<string, string>;
  bds_selector: Array<Array<Record<string, Array<string>>>>;
  action_card: Record<string, Record<string, ActionCard>>;
  action_name: Record<string, string>;
}

// ----------------------------------------------------------------------------

export interface LogicStatePlayer {
  budget: number;
  at: string;
  jail_stack: number;
  double_stack: number;
  alive: boolean;
}

export interface LogicStateBDS {
  owner?: string;
  level: number;
}

export interface LogicStateBuild {
  house: number;
  hotel: number;
  skyscraper: number;
}

export interface LogicStateAction {
  owner?: string;
}

// ----------------------------------------------------------------------------

export interface DiceCState { }
export interface DiceXbState { }

// ----------------------------------------------------------------------------

export interface GameLogicState {
  classic: boolean;

  bds: Record<string, LogicStateBDS>;
  player: Record<string, LogicStatePlayer>;
  current_player: string;
  viewing_player?: string;
  build: LogicStateBuild;
  action_card: Record<string, string[]>;
  rent_multiplier: number;
  steps?: number;
  action: Record<string, Record<string, LogicStateAction>>;
}


// ----------------------------------------------------------------------------

export interface UiStatePlayer {
  total: number
}

export interface UiStateBDS {
  level: number;
  can_upgrade?: boolean;
  can_downgrade?: boolean;
  can_mortgage: boolean;
  can_unmortgage: boolean;
  upgrade_amount?: number;
  downgrade_amount?: number;
  mortgage_amount?: number;
  unmortgage_amount?: number;
  can_choose: boolean;
}

export interface UiStateAction {
  can_use: boolean;
  can_choose: boolean;
}

// ----------------------------------------------------------------------------

export interface GameUiState {
  bds: Record<string, UiStateBDS>
  player: Record<string, UiStatePlayer>
  action: Record<string, Record<string, UiStateAction>>;
}

// ----------------------------------------------------------------------------

interface MovementLine {
  arrow: boolean
  start: string
  end: string
}

// ----------------------------------------------------------------------------

export interface GameEffectState {
  bds_enabled: boolean;
  can_trade: boolean;
  wait_ms: number;
  movement_lines: MovementLine[];
  dice_1?: string;
  dice_2?: string;
  dice_3?: string;
  speed_dice?: string;
  board?: number;
  select_bds?: string;
}

// ----------------------------------------------------------------------------

export interface GameState {
  turns?: number;
  logic: GameLogicState;
  ui: GameUiState;
  effect: GameEffectState;
  chore: Chore;
  current_chore: CurrentChore;
}

// ----------------------------------------------------------------------------
