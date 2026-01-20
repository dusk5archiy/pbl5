export interface Card {
  title: string;
  content: string;
}

export interface BDS {
  group: string;
  name: string;
  price: number;
  rent: number[];
  mortgage: number;
  upgrade?: number;
}

export interface ColorPalette {
  groups: Record<string, string>;
  border: string;
  spaces: Record<string, string>;
  cards: Record<string, string>;
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
}

export interface GameDataResponse {
  game_data: GameData;
}
