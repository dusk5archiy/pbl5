// Board color data from Python bco.py
export const PROPERTY_COLORS = {
  // Layer 2
  A: '#C98FCF',
  B: '#9A7340',
  C: '#F2BC6C',
  D: '#D6F2EF',
  E: '#14BC3C',
  F: '#5FB7FE',
  G: '#FFB3FF',
  H: '#F59469',
} as const;

// Board layout constants
export const BOARD_COLORS = {
  BROWN: '#8B4513',
  OUTL: '#8B4513',
  CO1: '#FFFFFF',
  CCH: 'lightpink',  // Tax spaces
  CKV: 'gold',       // Card spaces
  CVX: 'lightblue',  // Special spaces
} as const;

// Space codes in order (from Python banco_kihieu_o)
export const BANCO_KIHIEU_O = [
  'A1', 'A2',
  'TTN', 'R1', 'B1',
  'B2', 'B3', 'C1',
  'U1', 'C2', 'C3',
  'R1', 'D1', 'D2',
  'D3', 'E1', 'E2',
  'E3', 'R2A', 'F1',
  'F2', 'U2', 'F3',
  'G1', 'G2', 'G3',
  'R2', 'H1', 'TDB',
  'H2', '', '',
];

// Special spaces (from Python o_dacbiet_kihieu and o_dacbiet_ten)
export const SPECIAL_SPACES: Record<string, string> = {
  'VT': 'Vào Tù',
};

// Property data - properties that have names and prices
export const PROPERTY_DATA: Record<string, { name: string; price: number }> = {
  'A1': { name: 'NGUYỄN HUỆ', price: 60 },
  'A2': { name: 'LÊ LỢI', price: 80 },
  'B1': { name: 'LƯƠNG ĐỊNH CỦA', price: 100 },
  'B2': { name: 'VÕ THỊ SÁU', price: 100 },
  'B3': { name: 'HAI BÀ TRƯNG', price: 120 },
  'C1': { name: 'NGUYỄN TẤT THÀNH', price: 140 },
  'C2': { name: 'NGUYỄN TRÃI', price: 140 },
  'C3': { name: 'AN DƯƠNG VƯƠNG', price: 160 },
  'D1': { name: 'HẬU GIANG', price: 180 },
  'D2': { name: 'HÙNG VƯƠNG', price: 180 },
  'D3': { name: 'HUỲNH TẤN PHÁT', price: 200 },
  'E1': { name: 'PHẠM THỂ HIỂN', price: 220 },
  'E2': { name: 'KHA VẠNG CÂN', price: 220 },
  'E3': { name: 'NGUYỄN TRI PHƯƠNG', price: 240 },
  'F1': { name: 'LÊ ĐẠI HÀNH', price: 260 },
  'F2': { name: 'TRƯỜNG CHINH', price: 260 },
  'F3': { name: 'HOÀNG VĂN THỤ', price: 280 },
  'G1': { name: 'CỘNG HOÀ', price: 300 },
  'G2': { name: 'NGUYỄN KIỆM', price: 300 },
  'G3': { name: 'QUANG TRUNG', price: 320 },
  'H1': { name: 'LUỸ BÁN BÍCH', price: 350 },
  'H2': { name: 'TÂN KỲ TÂN QUÝ', price: 400 },
  'R1': { name: 'ĐƯỜNG SẮT HÀ NỘI', price: 200 },
  'R2': { name: 'ĐƯỜNG SẮT SÀI GÒN', price: 200 },
  'R3': { name: 'ĐƯỜNG SẮT HẢI PHÒNG', price: 200 },
  'R4': { name: 'ĐƯỜNG SẮT ĐÀ NẴNG', price: 200 },
  'U1': { name: 'CÔNG TY ĐIỆN LỰC', price: 150 },
  'U2': { name: 'CÔNG TY CẤP NƯỚC', price: 150 },
};
