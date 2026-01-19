// Game logic for Monopoly Impact

export interface DiceRoll {
  x1: number; // First die (1-6)
  x2: number; // Second die (1-6)
  x3: number; // Third die (1-6, where 4=Logo, 5=Logo, 6=Bus)
}

export interface PlayerState {
  position: string; // Current space code
  color: string;
  inJail: boolean;
  jailTurns: number;
  doubleCount: number; // Track consecutive doubles
  tunnelState: number; // 0 = normal, 1 = in tunnel
}

// Paths from Python bco.py
export const MAIN_PATH = [
  'BD','2A1','2KV1','2A2','TTN','1R1A','1B1','1B2','1CH1',
  '1U1','1B3','1B4','DH1','DGIA','1C1','1C2','1U2','1C3','1C4','1CH2',
  '1T2','1D1','1KV2','1D2','1D3','1D4','NTT','1E1','1CH3','1E2',
  '1E3','1E4','1T3','1R2','2F1','2F2','2U2','2F3','LAC3','2G1',
  '2G2','2KV3','2G3','2R2','DH','3B1','TCQL','3B2','3B3','3U1','3KV',
  '3C1','THUONG','3C2','3C3','2R1A','2D1','2KV2','2D2','2D3','BDX','2E1',
  '2CH2','2E2','2E3','1R2A','1KV3','1F1','1F2','1U3','1F3','1F4','VT',
  '1G1','1G2','1G3','1KV4','1G4','1VX2','1U4','1T4','QSN','1H1','1H2','1CH4',
  '1H3','TDN','1A1','1KV1','1A2','1A3','1VX1','1T1','1R1','2B1','2CH1','2B2',
  '2B3','TT','2C1','2U1','2C2','2C3','2R1','3D1','3D2','GDCP','3D3','HT',
  '3U2','3CH','3A1','DH2','3A2','3A3','2R2A','2CH3','2H1','TXX','2H2'
];

export const REVERSE_PATH = [
  'BD','2A1','2KV1','2A2','TTN','1R1A','1B1','1B2','1CH1',
  '1U1','1B3','1B4','DH1','DGIA','1C1','1C2','1U2','1C3','1C4','1CH2',
  '1T2','1D1','1KV2','1D2','1D3','1D4','NTT','1E1','1CH3','1E2',
  '1E3','1E4','1T3','1R2','2F1','2F2','2U2','2F3','LAC3','2G1',
  '2G2','2KV3','2G3','2R2','3A3','3A2','DH2','3A1','3CH','3U2','HT',
  '3D3','GDCP','3D2','3D1','2R1A','2D1','2KV2','2D2','2D3','BDX','2E1',
  '2CH2','2E2','2E3','1R2A','1KV3','1F1','1F2','1U3','1F3','1F4','VT',
  '1G1','1G2','1G3','1KV4','1G4','1VX2','1U4','1T4','QSN','1H1','1H2','1CH4',
  '1H3','TDN','1A1','1KV1','1A2','1A3','1VX1','1T1','1R1','2B1','2CH1','2B2',
  '2B3','TT','2C1','2U1','2C2','2C3','2R1','3C3','3C2','THUONG','3C1','3KV',
  '3U1','3B3','3B2','TCQL','3B1','DH','2R2A','2CH3','2H1','TXX','2H2'
];

export const TUNNEL_PATH_1 = [
  'NTT','1E1','1CH3','1E2','1E3','1E4','1T3','1R2',
  '1KV3','1F1','1F2','1U3','1F3','1F4','VT',
  '1G1','1G2','1G3','1KV4','1G4','1VX2','1U4','1T4','QSN','1H1','1H2','1CH4',
  '1H3','TDN','1A1','1KV1','1A2','1A3','1VX1','1T1','1R1','1B1','1B2','1CH1',
  '1U1','1B3','1B4','DH1','DGIA','1C1','1C2','1U2','1C3','1C4','1CH2',
  '1T2','1D1','1KV2','1D2','1D3','1D4'
];

export const TUNNEL_PATH_2 = [
  'BD','2A1','2KV1','2A2','TTN','1R1A','2B1','2CH1','2B2',
  '2B3','TT','2C1','2U1','2C2','2C3','2R1','2D1','2KV2','2D2','2D3','BDX','2E1',
  '2CH2','2E2','2E3','1R2A','2F1','2F2','2U2','2F3','LAC3','2G1',
  '2G2','2KV3','2G3','2R2','2CH3','2H1','TXX','2H2'
];

export const TUNNEL_PATH_3 = [
  'TCQL','3B2','3B3','3U1','3KV','3C1','THUONG','3C2','3C3','2R1A','3D1','3D2','GDCP','3D3','HT','3U2',
  '3CH','3A1','DH2','3A2','3A3','2R2A','DH','3B1'
];

export const TUNNEL_PATH_3_REVERSE = [
  '3C1', '3KV', '3U1', '3B3', '3B2', 'TCQL', '3B1', 'DH', '2R2A', '3A3', '3A2',
  'DH2', '3A1', '3CH', '3U2', 'HT', '3D3', 'GDCP', '3D2', '3D1', '2R1A', '3C3', '3C2', 'THUONG'
];

// Roll three dice
export function rollDice(): DiceRoll {
  return {
    x1: Math.floor(Math.random() * 6) + 1,
    x2: Math.floor(Math.random() * 6) + 1,
    x3: Math.floor(Math.random() * 6) + 1,
  };
}

// Check if it's a double
export function isDouble(roll: DiceRoll): boolean {
  const { x1, x2, x3 } = roll;
  
  // (x1==x2 AND x2≠x3) OR (x1==x2==x3 AND x3 in [4,5,6]) OR (x3 in [1,2,3] AND (x1==x3 OR x2==x3) AND x1≠x2)
  if (x1 === x2 && x2 !== x3) return true;
  if (x1 === x2 && x2 === x3 && x3 >= 4) return true;
  if (x3 <= 3 && (x1 === x3 || x2 === x3) && x1 !== x2) return true;
  
  return false;
}

// Calculate steps from dice roll
export function calculateSteps(roll: DiceRoll): number {
  const { x1, x2, x3 } = roll;
  
  // Three identical numbers (1, 2, or 3) - special case, no movement
  if (x1 === x2 && x2 === x3 && x3 <= 3) {
    return 0; // Special case - no movement
  }
  
  // Check for double: if it's a double, only use x1+x2
  const isDoubleRoll = isDouble(roll);
  if (isDoubleRoll) {
    return x1 + x2;
  }
  
  // Logo or Bus (x3 = 4, 5, or 6) - also only x1+x2
  if (x3 >= 4) {
    return x1 + x2; // Only first two dice
  }
  
  // Normal roll - use all three dice
  return x1 + x2 + x3; // All three dice
}

// Get the appropriate path based on steps and current position
export function getPath(steps: number, currentPosition: string, tunnelState: number): string[] {
  // Even steps: use main path or reverse path based on tunnel state
  if (steps % 2 === 0) {
    return tunnelState === 0 ? MAIN_PATH : REVERSE_PATH;
  }
  
  // Odd steps: determine which tunnel path based on current position
  if (TUNNEL_PATH_1.includes(currentPosition)) {
    return TUNNEL_PATH_1;
  } else if (TUNNEL_PATH_2.includes(currentPosition)) {
    return TUNNEL_PATH_2;
  } else {
    // Tunnel 3 or beyond: use tunnel 3 or reverse based on tunnel state
    return tunnelState === 0 ? TUNNEL_PATH_3 : TUNNEL_PATH_3_REVERSE;
  }
}

// Move player along path
export function movePlayer(currentPosition: string, steps: number, tunnelState: number): string[] {
  if (steps === 0) return [currentPosition];
  
  const path = getPath(steps, currentPosition, tunnelState);
  const currentIndex = path.indexOf(currentPosition);
  
  if (currentIndex === -1) {
    console.error('Current position not found in path:', currentPosition);
    return [currentPosition];
  }
  
  const positions: string[] = [];
  
  for (let i = 1; i <= steps; i++) {
    let newIndex = currentIndex + i;
    if (newIndex >= path.length) {
      newIndex -= path.length; // Wrap around
    }
    positions.push(path[newIndex]);
  }
  
  return positions;
}

// Format dice display
export function formatDiceDisplay(roll: DiceRoll): string {
  const { x1, x2, x3 } = roll;
  const x3Display = x3 === 4 || x3 === 5 ? 'C' : x3 === 6 ? 'XB' : x3;
  return `[${x1}, ${x2}, ${x3Display}]`;
}
