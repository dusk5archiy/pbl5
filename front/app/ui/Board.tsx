import React from 'react';
import { PlayerState } from './lib/gameLogic';
import { getSpacePosition } from './lib/positions';
import { Color } from './lib/colors';
import {
  PROPERTY_COLORS,
  BOARD_COLORS,
  BANCO_KIHIEU_O,
  SPECIAL_SPACES,
  PROPERTY_DATA
} from './lib/boardData';

// Based on Python Monopoly-Impact board layout from bco.py
// Board is 17x17 units, each unit = 40px = 680px total
export const DEFAULT_UNIT_SIZE = 35;

interface BoardProps {
  unitSize?: number;
  playerStates?: PlayerState[];
  movementLines?: { from: string, to: string, isLast?: boolean }[];
  highlightCircle?: { playerIndex: number, position: string } | null;
  currentPlayerColor?: Color;
}

// Board layout constants
const OUTL = BOARD_COLORS.OUTL;
const CO1 = BOARD_COLORS.CO1;
const CCH = BOARD_COLORS.CCH;
const CKV = BOARD_COLORS.CKV;

// Get label text for a space
const getLabelText = (code: string): string => {
  if (PROPERTY_DATA[code]) {
    return `${code.toUpperCase()}\n${PROPERTY_DATA[code].price}k`;
  } else if (SPECIAL_SPACES[code]) {
    return SPECIAL_SPACES[code];
  }
  return code;
};

// Get label color for a space (from Python mau_o_gtt)
const getLabelColor = (code: string): string => {
  if (code === 'THUONG') return 'green';
  if (code === 'BD') return '#FA0000';
  if (code === 'NTT') return 'blue';
  return 'black';
};

const Board: React.FC<BoardProps> = ({
  unitSize = DEFAULT_UNIT_SIZE,
  playerStates = [],
  // movementLines = [],
  // highlightCircle = null,
  // currentPlayerColor
}) => {
  const BOARD_SIZE = 17 * unitSize;

  // Position calculation (same as Python vt() function)
  const vt = (x: number): number => Math.floor((x * BOARD_SIZE) / 13);

  const fontSize = Math.floor(unitSize * 40 / 100);

  // Generate number sets (from Python banco_numberset1, 2, 3, 4)

  const banco_numberset2 = Array.from({ length: 9 }, (_, i) => vt(10.5 - i));
  const banco_numberset4 = [
    [12, 12], [5, 12], [5, 5], [12, 5],
    [3, 3], [14, 3], [14, 14], [3.375, 13.625],
    [2.375, 13.75], [3, 14.625], [1, 1], [16, 1],
    [16, 16], [1, 16]
  ];

  // Render all labels following the Python pattern
  const renderLabels = () => {
    const labels: React.ReactElement[] = [];
    let index = 0;

    // Helper to add a label
    const addLabel = (x: number, y: number) => {
      if (index >= BANCO_KIHIEU_O.length) return;
      const code = BANCO_KIHIEU_O[index];
      const text = getLabelText(code);
      const color = getLabelColor(code);

      // TT1 (Thăm) should be rotated 90 degrees (index 94 in the array)
      const shouldRotate = code === 'TT1';

      // Calculate vertical offset to center multi-line text
      const lines = text.split('\n');
      const lineCount = lines.length;
      const verticalOffset = (lineCount - 1) * fontSize / 2 - 4;

      labels.push(
        <text
          key={`label-${index}-${code}`}
          x={x}
          y={y - verticalOffset}
          textAnchor="middle"
          fontSize={fontSize}
          fill={color}
          fontFamily="Bahnschrift, Arial, sans-serif"
          fontWeight="normal"
          transform={shouldRotate ? `rotate(90, ${x}, ${y})` : undefined}
        >
          {lines.map((line, i) => (
            <tspan key={i} x={x} dy={i === 0 ? 0 : fontSize}>
              {line}
            </tspan>
          ))}
        </text>
      );
      index++;
    };

    // Bottom row (y = vt(16))
    let x = 0;
    let y = 0;
    // Layer 2 - Bottom row (y = vt(14))
    y = vt(12);
    for (const xPos of banco_numberset2) {
      if (![vt(9.5), vt(4.5)].includes(xPos)) {
        addLabel(xPos, y);
      }
    }

    // Layer 2 - Left column (x = vt(3))
    x = vt(1);
    for (const yPos of banco_numberset2) {
      if (![vt(4.5)].includes(yPos)) {
        addLabel(x, yPos);
      }
    }

    // Layer 2 - Top row (y = vt(3))
    y = vt(1);
    for (const xPos of [...banco_numberset2].reverse()) {
      if (![vt(3.5)].includes(xPos)) {
        addLabel(xPos, y);
      }
    }

    // Layer 2 - Right column (x = vt(14))
    x = vt(12);
    for (const yPos of [...banco_numberset2].reverse()) {
      if (![vt(4.5), vt(7.5)].includes(yPos)) {
        addLabel(x, yPos);
      }
    }
    // Special positions (banco_numberset4)
    for (const pos of banco_numberset4) {
      addLabel(vt(pos[0]), vt(pos[1]));
    }

    return labels;
  };

  // Get position coordinates for a space
  const getPositionCoords = (spaceCode: string): [number, number] => {
    const pos = getSpacePosition(spaceCode);
    if (!pos) {
      console.error('Position not found:', spaceCode);
      return [vt(8.5), vt(8.5)]; // Default to center
    }
    const [x, y] = pos;
    return [vt(x), vt(y)];
  };

  // Render player pieces
  const renderPieces = () => {
    // Map colors to image names
    const colorToImage: Record<string, string> = {
      'red': 'pldo',
      'orange': 'plcam',
      'yellow': 'plvang',
      'green': 'plluc',
      'blue': 'plxanh',
      'purple': 'pltim',
    };

    return playerStates.map((player, index) => {
      const posInfo = getSpacePosition(player.position);
      if (!posInfo) {
        console.error('Position not found for player', index, ':', player.position);
        return null;
      }

      const [x, y] = getPositionCoords(player.position);
      const pieceSize = unitSize * 0.6; // Slightly larger to match Python

      // In Python, pieces are placed at same location, no offset
      // All pieces at vt(14), vt(14.6) initially

      // Check if position is on vertical edge (left or right side)
      // Based on Python: is_vertical_edge flag determines image variant
      const isVerticalEdge = (posInfo[0] <= 2.5 || posInfo[0] >= 14.5) ? 1 : 0;

      const imageName = colorToImage[player.color] || 'pldo';
      const imageFile = isVerticalEdge ? `${imageName}2.png` : `${imageName}.png`;

      return (
        <image
          key={`piece-${index}`}
          x={x - pieceSize / 2}
          y={y - pieceSize / 2}
          width={pieceSize}
          height={pieceSize}
          href={`/img/${imageFile}`}
        />
      );
    });
  };

  return (
    <div>
      <svg
        width={BOARD_SIZE}
        height={BOARD_SIZE}
      // style={{ backgroundColor: '#2E6C3D' }}
      >
        {/* Pattern definitions (equivalent to Tkinter stipple) */}
        <defs>
          {/* Warning pattern - diagonal lines */}
          <pattern id="warning" patternUnits="userSpaceOnUse" width="4" height="4">
            <path d="M-1,1 l2,-2 M0,4 l4,-4 M3,5 l2,-2" stroke="rgba(0,0,0,0.3)" strokeWidth="0.5" />
          </pattern>

          {/* Gray25 pattern - 25% dotted */}
          <pattern id="gray25" patternUnits="userSpaceOnUse" width="2" height="2">
            <rect width="1" height="1" fill="rgba(0,0,0,0.25)" />
            <rect x="1" y="1" width="1" height="1" fill="rgba(0,0,0,0.25)" />
          </pattern>
        </defs>

        {/* LAYER 2: Middle layer (2-15) */}
        <rect x={vt(0)} y={vt(0)} width={vt(13)} height={vt(13)} fill={CO1} stroke={OUTL} strokeWidth="1" />
        <rect x={vt(2)} y={vt(2)} width={vt(11)} height={vt(11)} fill="lightgreen" stroke="brown" strokeWidth="1" />

        {/* Four corners */}
        <rect x={vt(0)} y={vt(0)} width={vt(2)} height={vt(2)} fill={CO1} stroke={OUTL} strokeWidth="1" />
        <rect x={vt(11)} y={vt(0)} width={vt(2)} height={vt(2)} fill={CO1} stroke={OUTL} strokeWidth="1" />
        <rect x={vt(0)} y={vt(11)} width={vt(2)} height={vt(2)} fill={CO1} stroke={OUTL} strokeWidth="1" />
        <rect x={vt(11)} y={vt(11)} width={vt(2)} height={vt(2)} fill={CO1} stroke={OUTL} strokeWidth="1" />

        {/* Perimeter strips - Layer 2 */}
        {Array.from({ length: 9 }, (_, i) => i + 2).map(i => (
          <g key={`middle-strip-${i}`}>
            <rect x={vt(0)} y={vt(i)} width={vt(2)} height={vt(1)} fill={CO1} stroke={OUTL} strokeWidth="1" />
            <rect x={vt(11)} y={vt(i)} width={vt(2)} height={vt(1)} fill={CO1} stroke={OUTL} strokeWidth="1" />
            <rect x={vt(i)} y={vt(0)} width={vt(1)} height={vt(2)} fill={CO1} stroke={OUTL} strokeWidth="1" />
            <rect x={vt(i)} y={vt(11)} width={vt(1)} height={vt(2)} fill={CO1} stroke={OUTL} strokeWidth="1" />
          </g>
        ))}

        {/* Property color strips - Layer 2 */}
        {[8, 10].map(i => (
          <rect key={`c2a-${i}`} x={vt(i)} y={vt(11)} width={vt(1)} height={vt(0.5)} fill={PROPERTY_COLORS.A} stroke={OUTL} strokeWidth="1" />
        ))}
        {[2, 3, 5].map(i => (
          <rect key={`c2b-${i}`} x={vt(i)} y={vt(11)} width={vt(1)} height={vt(0.5)} fill={PROPERTY_COLORS.B} stroke={OUTL} strokeWidth="1" />
        ))}
        {[2, 4, 5].map(i => (
          <rect key={`c2e-${i}`} x={vt(i)} y={vt(1.5)} width={vt(1)} height={vt(0.5)} fill={PROPERTY_COLORS.E} stroke={OUTL} strokeWidth="1" />
        ))}
        {[7, 8, 10].map(i => (
          <rect key={`c2f-${i}`} x={vt(i)} y={vt(1.5)} width={vt(1)} height={vt(0.5)} fill={PROPERTY_COLORS.F} stroke={OUTL} strokeWidth="1" />
        ))}
        {[7, 8, 10].map(i => (
          <rect key={`c2c-${i}`} x={vt(1.5)} y={vt(i)} width={vt(0.5)} height={vt(1)} fill={PROPERTY_COLORS.C} stroke={OUTL} strokeWidth="1" />
        ))}
        {[2, 3, 5].map(i => (
          <rect key={`c2d-${i}`} x={vt(1.5)} y={vt(i)} width={vt(0.5)} height={vt(1)} fill={PROPERTY_COLORS.D} stroke={OUTL} strokeWidth="1" />
        ))}
        {[2, 3, 5].map(i => (
          <rect key={`c2g-${i}`} x={vt(11)} y={vt(i)} width={vt(0.5)} height={vt(1)} fill={PROPERTY_COLORS.G} stroke={OUTL} strokeWidth="1" />
        ))}
        {[8, 10].map(i => (
          <rect key={`c2h-${i}`} x={vt(11)} y={vt(i)} width={vt(0.5)} height={vt(1)} fill={PROPERTY_COLORS.H} stroke={OUTL} strokeWidth="1" />
        ))}

        {/* Special spaces - Layer 2 */}
        {/* TT */} <rect x={vt(0.75)} y={vt(11)} width={vt(1.25)} height={vt(1.25)} fill="orange" stroke={OUTL} strokeWidth="1" />
        {/* CH1 */} <rect x={vt(4)} y={vt(11)} width={vt(1)} height={vt(2)} fill={CCH} stroke={OUTL} strokeWidth="1" />
        {/* CH1 */} <rect x={vt(4)} y={vt(11)} width={vt(1)} height={vt(2)} fill="url(#warning)" stroke={OUTL} strokeWidth="1" />
        {/* KV1 */} <rect x={vt(9)} y={vt(11)} width={vt(1)} height={vt(2)} fill={CKV} stroke={OUTL} strokeWidth="1" />
        {/* KV1 */} <rect x={vt(9)} y={vt(11)} width={vt(1)} height={vt(2)} fill="url(#warning)" stroke={OUTL} strokeWidth="1" />
        {/* CH2 */} <rect x={vt(3)} y={vt(0)} width={vt(1)} height={vt(2)} fill={CCH} stroke={OUTL} strokeWidth="1" />
        {/* CH2 */} <rect x={vt(3)} y={vt(0)} width={vt(1)} height={vt(2)} fill="url(#warning)" stroke={OUTL} strokeWidth="1" />
        {/* KV2 */} <rect x={vt(0)} y={vt(4)} width={vt(2)} height={vt(1)} fill={CKV} stroke={OUTL} strokeWidth="1" />
        {/* KV2 */} <rect x={vt(0)} y={vt(4)} width={vt(2)} height={vt(1)} fill="url(#warning)" stroke={OUTL} strokeWidth="1" />
        {/* CH3 */} <rect x={vt(11)} y={vt(7)} width={vt(2)} height={vt(1)} fill={CCH} stroke={OUTL} strokeWidth="1" />
        {/* CH3 */} <rect x={vt(11)} y={vt(7)} width={vt(2)} height={vt(1)} fill="url(#warning)" stroke={OUTL} strokeWidth="1" />
        {/* KV3 */} <rect x={vt(11)} y={vt(4)} width={vt(2)} height={vt(1)} fill={CKV} stroke={OUTL} strokeWidth="1" />
        {/* KV3 */} <rect x={vt(11)} y={vt(4)} width={vt(2)} height={vt(1)} fill="url(#warning)" stroke={OUTL} strokeWidth="1" />
        {/* U1 */} <rect x={vt(0.5)} y={vt(9.1)} width={vt(1)} height={vt(0.8)} fill="#DDEBFF" stroke="white" strokeWidth="1" />
        {/* U2 */} <rect x={vt(9.1)} y={vt(0.5)} width={vt(0.8)} height={vt(1)} fill="#DDEBFF" stroke="white" strokeWidth="1" />

        <rect x={vt(6)} y={vt(0)} width={vt(1)} height={vt(2)} fill="url(#gray25)" stroke={OUTL} strokeWidth="1" />
        <rect x={vt(6)} y={vt(11)} width={vt(1)} height={vt(2)} fill="url(#gray25)" stroke={OUTL} strokeWidth="1" />
        <rect x={vt(0)} y={vt(6)} width={vt(2)} height={vt(1)} fill="url(#gray25)" stroke={OUTL} strokeWidth="1" />
        <rect x={vt(11)} y={vt(6)} width={vt(2)} height={vt(1)} fill="url(#gray25)" stroke={OUTL} strokeWidth="1" />

        {/* Border line for inner area - Layer 2 */}
        <line x1={vt(2)} y1={vt(2)} x2={vt(2)} y2={vt(11)} stroke="grey" strokeWidth="5" />
        <line x1={vt(2)} y1={vt(11)} x2={vt(11)} y2={vt(11)} stroke="grey" strokeWidth="5" />
        <line x1={vt(11)} y1={vt(11)} x2={vt(11)} y2={vt(2)} stroke="grey" strokeWidth="5" />
        <line x1={vt(11)} y1={vt(2)} x2={vt(2)} y2={vt(2)} stroke="grey" strokeWidth="5" />

        {/* Labels for all spaces */}
        {renderLabels()}

        {/* Movement lines */}
        {/* {movementLines?.map((line, index) => { */}
        {/*   const fromPos = getSpacePosition(line.from); */}
        {/*   const toPos = getSpacePosition(line.to); */}
        {/**/}
        {/*   if (!fromPos) { */}
        {/*     console.error('Position not found for "from":', line.from); */}
        {/*     return null; */}
        {/*   } */}
        {/*   if (!toPos) { */}
        {/*     console.error('Position not found for "to":', line.to); */}
        {/*     return null; */}
        {/*   } */}
        {/**/}
        {/*   const [fromX, fromY] = fromPos; */}
        {/*   const [toX, toY] = toPos; */}
        {/*   const x1 = vt(fromX); */}
        {/*   const y1 = vt(fromY); */}
        {/*   const x2 = vt(toX); */}
        {/*   const y2 = vt(toY); */}
        {/**/}
        {/*   return ( */}
        {/*     <line */}
        {/*       key={`${line.from}-${line.to}-${index}`} */}
        {/*       x1={x1} */}
        {/*       y1={y1} */}
        {/*       x2={x2} */}
        {/*       y2={y2} */}
        {/*       stroke="black" */}
        {/*       strokeWidth="1" */}
        {/*       strokeLinecap="round" */}
        {/*       opacity="0.8" */}
        {/*       markerEnd={line.isLast ? 'url(#arrowhead)' : undefined} */}
        {/*     /> */}
        {/*   ); */}
        {/* })} */}

        {/* Highlight circle around current piece */}
        {/* {highlightCircle && (() => { */}
        {/*   const pos = getSpacePosition(highlightCircle.position); */}
        {/**/}
        {/*   if (!pos) { */}
        {/*     console.error('Position not found for highlight circle:', highlightCircle.position); */}
        {/*     return null; */}
        {/*   } */}
        {/**/}
        {/*   // Python color3 array from bco.py line 345: ['red','darkorange','goldenrod','green','blue','magenta'] */}
        {/*   // Maps player colors to their circle colors (matching Python's color3 array order) */}
        {/*   const colorToCircleColor: Record<string, string> = { */}
        {/*     'red': 'red',           // Player 0 */}
        {/*     'orange': 'darkorange', // Player 1 */}
        {/*     'yellow': 'goldenrod',  // Player 2 */}
        {/*     'green': 'green',       // Player 3 */}
        {/*     'blue': 'blue',         // Player 4 */}
        {/*     'purple': 'magenta',    // Player 5 */}
        {/*   }; */}
        {/**/}
        {/*   const playerColor = playerStates?.[highlightCircle.playerIndex]?.color || 'red'; */}
        {/*   const circleColor = colorToCircleColor[playerColor] || 'red'; */}
        {/**/}
        {/*   const [posX, posY] = pos; */}
        {/*   const x = vt(posX); */}
        {/*   const y = vt(posY); */}
        {/*   const radius = vt(40 / (BOARD_SIZE / 17)); // Python uses radius 40 on board size si17 */}
        {/**/}
        {/*   return ( */}
        {/*     <circle */}
        {/*       cx={x} */}
        {/*       cy={y} */}
        {/*       r={radius} */}
        {/*       fill="none" */}
        {/*       stroke={circleColor} */}
        {/*       strokeWidth="5" */}
        {/*     /> */}
        {/*   ); */}
        {/* })()} */}

        {/* Player pieces */}
        {/* {renderPieces()} */}

        {/* Arrow marker definition for last line */}
        {/* <defs> */}
        {/*   <marker */}
        {/*     id="arrowhead" */}
        {/*     markerWidth="5" */}
        {/*     markerHeight="5" */}
        {/*     refX="4" */}
        {/*     refY="2.5" */}
        {/*     orient="auto" */}
        {/*   > */}
        {/*     <polygon */}
        {/*       points="0 0, 5 2.5, 0 5" */}
        {/*       fill="black" */}
        {/*     /> */}
        {/*   </marker> */}
        {/* </defs> */}
      </svg>
    </div>
  );
};

export default Board;
