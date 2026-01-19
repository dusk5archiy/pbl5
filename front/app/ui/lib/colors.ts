export enum Color {
  Red = 'red',
  Orange = 'orange',
  Yellow = 'yellow',
  Blue = 'blue',
  Green = 'green',
  Purple = 'purple',
}

export const colorTranslations: Record<Color, string> = {
  [Color.Red]: 'Đỏ',
  [Color.Orange]: 'Cam',
  [Color.Yellow]: 'Vàng',
  [Color.Blue]: 'Xanh',
  [Color.Green]: 'Lục',
  [Color.Purple]: 'Tím',
};

// Exact colors from Python var.py (matching the game logic)
export const PYTHON_PLAYER_COLORS = [
  '#FF8B8B', // Player 0 - Red
  '#FFC000', // Player 1 - Orange
  'yellow', // Player 2 - Yellow
  '#B1FFAB', // Player 3 - Light Green
  '#B7F3FF', // Player 4 - Light Blue
  '#EEBBFF', // Player 5 - Light Purple
];

// Map Color enum to Python hex colors
export const COLOR_TO_HEX: Record<Color, string> = {
  [Color.Red]: '#FF8B8B',
  [Color.Orange]: '#FFC000',
  [Color.Yellow]: 'yellow',
  [Color.Green]: '#B1FFAB',
  [Color.Blue]: '#B7F3FF',
  [Color.Purple]: '#EEBBFF',
};

// Property group colors from Python bco.py
export const PROPERTY_GROUP_COLORS: Record<string, string> = {
  'C1A': '#BAD191', // Light green - Nguyễn Du group
  'C1B': '#C7CCE3', // Light blue - Kim Đồng group
  'C1C': '#71EDE1', // Cyan - Nguyễn Hữu Thọ group
  'C1D': '#FFF24F', // Yellow - Trưng Nữ Vương group
  'C1E': '#F46A95', // Pink - Hàm Nghi group
  'C1F': '#F0F7D5', // Light green - Nguyễn Bỉnh Khiêm group
  'C1G': '#97FF8F', // Light green - Phan Bội Châu group
  'C1H': '#AC9FFB', // Light purple - Trần Hưng Đạo group
  'C2A': '#C98FCF', // Purple
  'C2B': '#9A7340', // Brown
  'C2C': '#F2BC6C', // Orange
  'C2D': '#D6F2EF', // Light cyan
  'C2E': '#14BC3C', // Green
  'C2F': '#5FB7FE', // Blue
  'C2G': '#FFB3FF', // Pink
  'C2H': '#F59469', // Orange
  'C3A': '#B4D200', // Lime
  'C3B': '#6CFCDA', // Cyan
  'C3C': '#FFB92D', // Orange
  'C3D': '#FF5DBA', // Pink
};