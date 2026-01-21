import React from 'react';
import { PlayerState } from './lib/gameLogic';
// import { getSpacePosition } from './lib/positions';
import { Color } from './lib/colors';
import { GameData, GameState } from '@/app/game/model';
import { formatBudget } from './lib/utils';

export const DEFAULT_UNIT_SIZE = 45;

interface BoardProps {
  unitSize?: number;
  playerStates?: PlayerState[];
  movementLines?: { from: string, to: string, isLast?: boolean }[];
  highlightCircle?: { playerIndex: number, position: string } | null;
  currentPlayerColor?: Color;
  gameData: GameData;
  gameState: GameState
}

// Board layout constants
// const OUTL = BOARD_COLORS.OUTL;
// const CO1 = BOARD_COLORS.CO1;
// const CCH = BOARD_COLORS.CCH;
// const CKV = BOARD_COLORS.CKV;

// Get label text for a space
// const getLabelText = (code: string): string => {
//   return code;
// };

// Get label color for a space (from Python mau_o_gtt)
// const getLabelColor = (code: string): string => {
//   if (code === 'THUONG') return 'green';
//   if (code === 'BD') return '#FA0000';
//   if (code === 'NTT') return 'blue';
//   return 'black';
// };

const Board: React.FC<BoardProps> = ({
  unitSize = DEFAULT_UNIT_SIZE,
  // playerStates = [],
  // movementLines = [],
  // highlightCircle = null,
  // currentPlayerColor
  gameData,
  gameState
}) => {
  // Board layout constants
  const vt_max = gameData.vt_max;
  const BOARD_SIZE = vt_max * unitSize;

  const vt = (x: number): number => x * unitSize;
  const fontSize = Math.floor(unitSize * 0.35);

  // Generate number sets (from Python banco_numberset1, 2, 3, 4)

  // const banco_numberset2 = Array.from({ length: 9 }, (_, i) => vt(10.5 - i));
  // const banco_numberset4 = [
  //   [12, 12], [5, 12], [5, 5], [12, 5],
  //   [3, 3], [14, 3], [14, 14], [3.375, 13.625],
  //   [2.375, 13.75], [3, 14.625], [1, 1], [16, 1],
  //   [16, 16], [1, 16]
  // ];

  // Render all labels following the Python pattern
  // const renderLabels = () => {
  //   const labels: React.ReactElement[] = [];
  // let index = 0;

  // Helper to add a label
  // const addLabel = (x: number, y: number) => {
  //   if (index >= BANCO_KIHIEU_O.length) return;
  //   const code = BANCO_KIHIEU_O[index];
  //   const text = getLabelText(code);
  //   const color = getLabelColor(code);
  //
  //   // TT1 (Thăm) should be rotated 90 degrees (index 94 in the array)
  //   const shouldRotate = code === 'TT1';
  //
  //   // Calculate vertical offset to center multi-line text
  //   const lines = text.split('\n');
  //   const lineCount = lines.length;
  //   const verticalOffset = (lineCount - 1) * fontSize / 2 - 4;
  //
  //   labels.push(
  //     <text
  //       key={`label-${index}-${code}`}
  //       x={x}
  //       y={y - verticalOffset}
  //       textAnchor="middle"
  //       fontSize={fontSize}
  //       fill={color}
  //       fontFamily="Bahnschrift, Arial, sans-serif"
  //       fontWeight="normal"
  //       transform={shouldRotate ? `rotate(90, ${x}, ${y})` : undefined}
  //     >
  //       {lines.map((line, i) => (
  //         <tspan key={i} x={x} dy={i === 0 ? 0 : fontSize}>
  //           {line}
  //         </tspan>
  //       ))}
  //     </text>
  //   );
  //   index++;
  // };

  // let x = 0;
  // let y = 0;
  // Bottom side
  // y = vt(12);
  // for (const xPos of banco_numberset2) {
  //   if (![vt(9.5), vt(4.5)].includes(xPos)) {
  //     addLabel(xPos, y);
  //   }
  // }

  // Left side
  // x = vt(1);
  // for (const yPos of banco_numberset2) {
  //   if (![vt(4.5)].includes(yPos)) {
  //     addLabel(x, yPos);
  //   }
  // }

  // Top side
  // y = vt(1);
  // for (const xPos of [...banco_numberset2].reverse()) {
  //   if (![vt(3.5)].includes(xPos)) {
  //     addLabel(xPos, y);
  //   }
  // }
  //
  // Right side
  // x = vt(12);
  // for (const yPos of [...banco_numberset2].reverse()) {
  //   if (![vt(4.5), vt(7.5)].includes(yPos)) {
  //     addLabel(x, yPos);
  //   }
  // }
  // Special positions (banco_numberset4)
  // for (const pos of banco_numberset4) {
  //   addLabel(vt(pos[0]), vt(pos[1]));
  // }
  //
  //   return labels;
  // };

  // Get position coordinates for a space
  // const getPositionCoords = (spaceCode: string): [number, number] => {
  //   const pos = getSpacePosition(spaceCode);
  //   if (!pos) {
  //     console.error('Position not found:', spaceCode);
  //     return [vt(8.5), vt(8.5)]; // Default to center
  //   }
  //   const [x, y] = pos;
  //   return [vt(x), vt(y)];
  // };

  // Render player pieces
  // const renderPieces = () => {
  //   // Map colors to image names
  //   const colorToImage: Record<string, string> = {
  //     'red': 'pldo',
  //     'orange': 'plcam',
  //     'yellow': 'plvang',
  //     'green': 'plluc',
  //     'blue': 'plxanh',
  //     'purple': 'pltim',
  //   };
  //
  //   return playerStates.map((player, index) => {
  //     const posInfo = getSpacePosition(player.position);
  //     if (!posInfo) {
  //       console.error('Position not found for player', index, ':', player.position);
  //       return null;
  //     }
  //
  //     const [x, y] = getPositionCoords(player.position);
  //     const pieceSize = unitSize * 0.6; // Slightly larger to match Python
  //
  //     // In Python, pieces are placed at same location, no offset
  //     // All pieces at vt(14), vt(14.6) initially
  //
  //     // Check if position is on vertical edge (left or right side)
  //     // Based on Python: is_vertical_edge flag determines image variant
  //     const isVerticalEdge = (posInfo[0] <= 2.5 || posInfo[0] >= 14.5) ? 1 : 0;
  //
  //     const imageName = colorToImage[player.color] || 'pldo';
  //     const imageFile = isVerticalEdge ? `${imageName}2.png` : `${imageName}.png`;
  //
  //     return (
  //       <image
  //         key={`piece-${index}`}
  //         x={x - pieceSize / 2}
  //         y={y - pieceSize / 2}
  //         width={pieceSize}
  //         height={pieceSize}
  //         href={`/img/${imageFile}`}
  //       />
  //     );
  //   });
  // };

  const border = gameData.color_pallete.border;

  const orient_to_wh = (orient: string) => {
    switch (orient) {
      case "S":
      case "N":
        return { w: vt(1), h: vt(2) };
      case "W":
      case "E":
        return { w: vt(2), h: vt(1) };
      case "NE":
      case "SE":
      case "SW":
      case "NW":
      default:
        return { w: vt(2), h: vt(2) };
    }
  }

  const orient_to_wh_banner = (orient: string) => {
    switch (orient) {
      case "S":
      case "N":
        return { w: vt(1), h: vt(0.5) };
      case "W":
      case "E":
      default:
        return { w: vt(0.5), h: vt(1) };
    }
  }

  const orient_to_offset_label = (orient: string) => {
    switch (orient) {
      case "S":
      case "N":
        return { w: 0.5, h: 1 };
      case "W":
      case "E":
      default:
        return { w: 1, h: 0.5 };
    }
  }

  const drawSpace = (spaceId: string) => {
    const space = gameData.space[spaceId];
    const { w, h } = orient_to_wh(space.orient);
    return (
      <rect
        key={spaceId}
        x={vt(space.x)}
        y={vt(space.y)}
        width={w}
        height={h}
        fill="white"
        stroke={border}
        strokeWidth="1"
      />
    )
  }

  const drawNormalBDSBanner = (spaceId: string) => {
    const group = gameData.bds[spaceId].group;
    const space = gameData.space[spaceId];
    const { w, h } = orient_to_wh_banner(space.orient);
    switch (space.orient) {
      case "S":
      case "E":
        return (
          <rect key={spaceId} x={vt(space.x)} y={vt(space.y)} width={w} height={h} fill={gameData.color_pallete.groups[group]} stroke={border} strokeWidth="1" />
        );
      case "N":
        return (
          <rect key={spaceId} x={vt(space.x)} y={vt(space.y + 1.5)} width={w} height={h} fill={gameData.color_pallete.groups[group]} stroke={border} strokeWidth="1" />
        );
      case "W":
      default:
        return (
          <rect key={spaceId} x={vt(space.x + 1.5)} y={vt(space.y)} width={w} height={h} fill={gameData.color_pallete.groups[group]} stroke={border} strokeWidth="1" />
        );
    }
  }
  const drawRBanner = (spaceId: string) => {
    const space = gameData.space[spaceId];
    const { w, h } = orient_to_wh(space.orient);
    return (
      <g key={`banner-${spaceId}`}>
        <rect x={vt(space.x)} y={vt(space.y)} width={w} height={h} fill="url(#gray25)" stroke={border} strokeWidth="1" />
        <rect x={vt(space.x)} y={vt(space.y)} width={w} height={h} fill="url(#gray25)" stroke={border} strokeWidth="1" />
      </g>
    );
  };

  const orient_to_u_offset = (orient: string) => {
    switch (orient) {
      case "S":
      case "N":
        return { off_w: 0.1, off_h: 0.5 };
      case "W":
      case "E":
      default:
        return { off_w: 0.5, off_h: 0.1 };
    }
  }

  const orient_to_u_wh = (orient: string) => {
    switch (orient) {
      case "S":
      case "N":
        return { w: vt(0.8), h: vt(1) };
      case "W":
      case "E":
      default:
        return { w: vt(1), h: vt(0.8) };
    }
  }


  const drawUBanner = (spaceId: string) => {
    const space = gameData.space[spaceId];
    const key = `banner-${spaceId}`;
    const { off_w, off_h } = orient_to_u_offset(space.orient);
    const { w, h } = orient_to_u_wh(space.orient);
    return (
      <rect key={key} x={vt(space.x + off_w)} y={vt(space.y + off_h)} width={w} height={h} fill={gameData.color_pallete.groups.U} stroke="white" strokeWidth="1" />
    );
  };

  const drawActionCardSpace = (spaceId: string) => {
    const space = gameData.space[spaceId];
    const group = gameData.special_spaces[spaceId]
    const { w, h } = orient_to_wh(space.orient);
    return (
      <g key={`action-card-${spaceId}`}>
        <rect x={vt(space.x)} y={vt(space.y)} width={w} height={h} fill={gameData.color_pallete.cards[group]} stroke={border} strokeWidth="1" />
        <rect x={vt(space.x)} y={vt(space.y)} width={w} height={h} fill="url(#warning)" stroke={border} strokeWidth="1" />
      </g>
    );
  }

  const OT_SPACE = gameData.space.OT;

  const drawTextLabel = (key: string, text: string, x: number, y: number, color: string, rotate: boolean = false) => {
    const lines = text.split('\n');
    const lineCount = lines.length;
    const verticalOffset = (lineCount - 1) * fontSize / 2 - 4;
    return (
      <text
        key={key}
        x={x}
        y={y - verticalOffset}
        textAnchor="middle"
        fontSize={fontSize}
        fill={color}
        fontFamily="Bahnschrift, Arial, sans-serif"
        fontWeight="normal"
        transform={rotate ? `rotate(90, ${x}, ${y})` : undefined}
      >
        {lines.map((line, i) => (
          <tspan key={i} x={x} dy={i === 0 ? 0 : fontSize}>
            {line}
          </tspan>
        ))}
      </text>
    );
  };

  const drawBDSLabel = (spaceId: string) => {
    const space = gameData.space[spaceId];
    const price = gameData.bds[spaceId].price;
    const text = `${spaceId}\n${formatBudget(price)}`;
    const { w, h } = orient_to_offset_label(space.orient);
    return drawTextLabel(`text-${spaceId}`, text, vt(space.x + w), vt(space.y + h), "black");

  };

  const drawBDAU = () => {
    const spaceId = "BDAU";
    const space = gameData.space[spaceId];
    const text = gameData.space_labels[spaceId];
    const color = gameData.color_pallete.spaces["BDAU"];
    return drawTextLabel(`text-${spaceId}`, text, vt(space.x + 1), vt(space.y + 1), color);
  }

  const drawCornerLabel = (spaceId: string) => {
    const space = gameData.space[spaceId];
    const text = gameData.space_labels[spaceId];
    return drawTextLabel(`text-${spaceId}`, text, vt(space.x + 1), vt(space.y + 1), "black");
  }

  const drawEdgeLabel = (spaceId: string) => {
    const space = gameData.space[spaceId];
    const text = gameData.space_labels[spaceId];
    const { w, h } = orient_to_offset_label(space.orient);
    return drawTextLabel(`text-${spaceId}`, text, vt(space.x + w), vt(space.y + h), "black");
  }

  const drawOT = () => {
    const spaceId = "OT";
    const space = gameData.space[spaceId];
    const text = gameData.space_labels[spaceId];
    return drawTextLabel(`text-${spaceId}`, text, vt(space.x + 0.625), vt(space.y + 0.7), "black");
  }

  const drawTT = () => {
    const space = gameData.space["TT"];
    return (
      <g key="tt-labels">
        {drawTextLabel(`text-TT1`, gameData.space_labels["TT1"], vt(space.x + 0.35), vt(space.y + 0.8), "black", true)}
        {drawTextLabel(`text-TT2`, gameData.space_labels["TT2"], vt(space.x + 1.25), vt(space.y + 1.625), "black")}
      </g>
    );
  }

  const orient_to_player_offset = (orient: string) => {
    switch (orient) {
      case "S":
        return { off_w: 0.5, off_h: 1.5 };
      case "SE":
        return { off_w: 1, off_h: 1.5 };
      default:
        return { off_w: 0, off_h: 0 };
    }
  }

  const drawPlayers = () => {
    const pieceSize = unitSize * 0.7;
    return Object.entries(gameState.players).map(([playerId, playerState]) => {
      const space = gameData.space[gameState.players[playerId].at];
      const { off_w, off_h } = orient_to_player_offset(space.orient);
      return (
        <image
          key={`player-${playerId}`}
          x={vt(space.x + off_w) - pieceSize / 2}
          y={vt(space.y + off_h) - pieceSize / 2}
          width={pieceSize}
          height={pieceSize}
          href={`/assets/players/${playerId}.png`}
        />
      );
    });
  };

  const drawCircle = () => {
    const playerId = gameState.current_player;
    const space = gameData.space[gameState.players[playerId].at];
    const { off_w, off_h } = orient_to_player_offset(space.orient);
    console.log(gameData.color_pallete.circle);
    return (
      <circle
        cx={vt(space.x + off_w)}
        cy={vt(space.y + off_h)}
        r={vt(1)}
        fill="none"
        stroke={gameData.color_pallete.circle[playerId]}
        strokeWidth="5"
      />
    );
  };

  return (
    <div>
      <svg
        width={BOARD_SIZE}
        height={BOARD_SIZE}
      >
        {/* Pattern definitions (equivalent to Tkinter stipple) */}
        <defs>
          {/* Warning pattern - diagonal lines */}
          <pattern id="warning" patternUnits="userSpaceOnUse" width="4" height="4">
            <path d="M-1,1 l2,-2 M0,4 l4,-4 M3,5 l2,-2" stroke="rgba(255,255,255,0.3)" strokeWidth="1.5" />
          </pattern>

          {/* Gray25 pattern - 25% dotted */}
          <pattern id="gray25" patternUnits="userSpaceOnUse" width="2" height="2">
            <rect width="1" height="1" fill="rgba(0,0,0,0.25)" />
            <rect x="1" y="1" width="1" height="1" fill="rgba(0,0,0,0.25)" />
          </pattern>
        </defs>

        <rect x={vt(0)} y={vt(0)} width={vt(vt_max)} height={vt(vt_max)} fill="#479777" stroke={border} strokeWidth="1" />
        {
          Object.keys(gameData.space)
            .filter(spaceId => spaceId !== "OT")
            .map(spaceId => drawSpace(spaceId)
            )
        }
        {
          Object.keys(gameData.space)
            .filter(spaceId => spaceId in gameData.bds)
            .map(spaceId => {
              const group = gameData.bds[spaceId].group;
              switch (group) {
                case "R":
                  return drawRBanner(spaceId);
                case "U":
                  return drawUBanner(spaceId);
                default:
                  return drawNormalBDSBanner(spaceId);
              }
            })
        }
        {
          Object.keys(gameData.space)
            .filter(spaceId => spaceId in gameData.special_spaces)
            .map(spaceId => drawActionCardSpace(spaceId))
        }
        <rect x={vt(OT_SPACE.x)} y={vt(OT_SPACE.y)} width={vt(1.25)} height={vt(1.25)} fill={gameData.color_pallete.spaces.OT} stroke={border} strokeWidth="1" />

        <line x1={vt(2)} y1={vt(2)} x2={vt(2)} y2={vt(vt_max - 2)} stroke="grey" strokeWidth="5" />
        <line x1={vt(2)} y1={vt(vt_max - 2)} x2={vt(11)} y2={vt(vt_max - 2)} stroke="grey" strokeWidth="5" />
        <line x1={vt(vt_max - 2)} y1={vt(vt_max - 2)} x2={vt(vt_max - 2)} y2={vt(2)} stroke="grey" strokeWidth="5" />
        <line x1={vt(vt_max - 2)} y1={vt(2)} x2={vt(2)} y2={vt(2)} stroke="grey" strokeWidth="5" />

        {
          Object.keys(gameData.space)
            .filter(spaceId => spaceId in gameData.bds)
            .map(spaceId => drawBDSLabel(spaceId))
        }
        {drawBDAU()}
        {drawCornerLabel("VT")}
        {drawCornerLabel("BDX")}
        {drawEdgeLabel("TDB")}
        {drawEdgeLabel("TTN")}
        {drawOT()}
        {drawTT()}
        {drawPlayers()}
        {drawCircle()}

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
