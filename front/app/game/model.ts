export interface Card {
  title: string;
  content: string;
  keep: boolean;
}

export interface BDS {
  group: string;
  name: string;
  price: number;
  rent: number[];
  mortgage: number;
  upgrade?: number;
  downgrade?: number;
  unmortgage: number;
}

export interface ColorPalette {
  groups: Record<string, string>;
  border: string;
  spaces: Record<string, string>;
  cards: Record<string, string>;
  players: Record<string, string>;
  circle: Record<string, string>;
}

export interface Space {
  orient: string;
  x: number;
  y: number;
}

export interface GameData {
  vt_max: number,
  kv: Record<string, Card>;
  ch: Record<string, Card>;
  bds: Record<string, BDS>;
  space: Record<string, Space>;
  track: string[];
  color_pallete: ColorPalette;
  space_labels: Record<string, string>;
  special_spaces: Record<string, string>;
  bds_groups_order: string[];
  group_bds: Record<string, string[]>;
}

export interface GameDataResponse {
  game_data: GameData;
}

export interface GameStatePlayer {
  budget: number;
  at: string;
  total: number;
}

export interface GameStateBDS {
  owner: string;
  level: number;
  can_upgrade: boolean;
  can_downgrade: boolean;
  can_mortgage: boolean;
  can_unmortgage: boolean;
}

export interface PendingAction {
  type: string;
  data: Record<string, any>;
}

export interface GameState {
  kv_queue: string[];
  ch_queue: string[];
  bds: Record<string, GameStateBDS>;
  cards: Record<string, string>;
  player_queue: string[];
  players: Record<string, GameStatePlayer>;
  current_player: string;
  double_roll_stack: number;
  pending_actions: PendingAction[];
  houses_left: number;
  hotels_left: number;
}
