export type ColorUIInfo = {
  uiName: string;
  lightColorCode: string;
  darkColorCode: string;
}
export const COLOR_UI_INFO: Record<string, ColorUIInfo> = {
  "red": { uiName: "Đỏ", lightColorCode: "#FF8B8B", darkColorCode: "red" },
  "orange": { uiName: "Cam", lightColorCode: "#FFC000", darkColorCode: "darkorange" },
  "yellow": { uiName: "Vàng", lightColorCode: "#FFF360", darkColorCode: "goldenrod" },
  "green": { uiName: "Lục", lightColorCode: "#B1FFAB", darkColorCode: "green" },
  "blue": { uiName: "Lam", lightColorCode: "#B7F3FF", darkColorCode: "blue" },
  "purple": { uiName: "Tím", lightColorCode: "#EEBBFF", darkColorCode: "magenta" },
}

export const BOARD_BG_COLOR = "#479777";
export const PROPERTY_DOCK_BG_COLOR = "#446655";
export const BORDER_COLOR = "#8B4513";
