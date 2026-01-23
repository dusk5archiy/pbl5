import React from 'react';
import { GameData, GameState } from '@/app/game/model';
import { formatBudget } from './lib/utils';

export const DEFAULT_UNIT_SIZE = 45;

interface BoardProps {
  movementLines?: { from: string, to: string, isLast?: boolean }[];
  gameData: GameData;
  gameState: GameState;
  message?: string;
}

const Board: React.FC<BoardProps> = ({
  movementLines = [],
  gameData,
  gameState,
  message
}) => {
  // Board layout constants
  const vt_max = gameData.vt_max;

  // vt() returns percentage string for responsive scaling
  const vt = (x: number) => `${x / vt_max * 100}%`;

  // vtNum() returns numeric percentage for attributes that need numbers
  const vtNum = (x: number) => (x / vt_max * 100);

  const fontSize = `${0.35 / vt_max * 100}vh`;
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

  const drawTextLabel = (key: string, text: string, x: string, y: string, color: string, rotate: boolean = false, fontFamily: string = "Bahnschrift, Arial, sans-serif", fontWeight: string = "normal") => {
    const lines = text.split('\n');
    const lineCount = lines.length;

    const verticalShift = -lineCount / 2 + 0.75;
    const translateY = `calc(${fontSize} * ${verticalShift})`;
    const transform = rotate
      ? `translate(0, ${translateY}) rotate(90deg)`
      : `translate(0, ${translateY})`;

    return (
      <text
        key={key}
        x={x}
        y={y}
        textAnchor="middle"
        fontSize={fontSize}
        fill={color}
        fontFamily={fontFamily}
        fontWeight={fontWeight}
        style={{
          transform,
          transformOrigin: rotate ? `${x} ${y}` : undefined
        }}
      >
        {lines.map((line, i) => (
          <tspan key={i} x={x} dy={i === 0 ? '0' : fontSize}>
            {line}
          </tspan>
        ))}
      </text>
    );
  };

  const drawBDSLabel = (spaceId: string) => {
    const space = gameData.space[spaceId];
    const bdsState = gameState.bds[spaceId];
    const isOwned = bdsState && bdsState.owner !== "";

    let text: string;
    let color: string;
    let fontFamily: string;
    let fontWeight: string;

    if (isOwned) {
      // Get player color index (0-5) for styling
      const playerColorIndex = Object.keys(gameData.color_pallete.players).indexOf(bdsState.owner);
      const colors = ['FireBrick', 'red', 'DarkGoldenRod', 'darkgreen', 'dodgerblue', 'purple'];
      const fonts = ['Cambria', 'Seaford', 'Itim', 'Seaford', 'Cambria', 'Itim'];

      color = colors[playerColorIndex] || 'black';
      fontFamily = fonts[playerColorIndex] || 'Bahnschrift, Arial, sans-serif';
      fontWeight = 'bold';

      const level = bdsState.level === -1 ? '-' : bdsState.level.toString();
      text = `${spaceId}\nLv.${level}`;
    } else {
      const price = gameData.bds[spaceId].price;
      text = `${spaceId}\n${formatBudget(price)}`;
      color = "black";
      fontFamily = "Bahnschrift, Arial, sans-serif";
      fontWeight = "normal";
    }

    const { w, h } = orient_to_offset_label(space.orient);
    return drawTextLabel(`text-${spaceId}`, text, vt(space.x + w), vt(space.y + h), color, false, fontFamily, fontWeight);
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
    const low = 0.4;
    const high = 1.6;
    switch (orient) {
      case "S":
        return { off_w: low, off_h: high };
      case "W":
        return { off_w: low, off_h: low };
      case "NW":
      case "NE":
        return { off_w: 1, off_h: low };
      case "N":
        return { off_w: low, off_h: low };
      case "E":
        return { off_w: high, off_h: low };
      case "SW":
      case "SE":
        return { off_w: 1, off_h: high };
      default:
        return { off_w: 0, off_h: 0 };
    }
  }

  const is_player_rotated = (orient: string) => {
    switch (orient) {
      case "S":
      case "SW":
      case "SE":
      case "N":
      case "NW":
      case "NE":
        return false;
      default: return true;
    }
  }

  const drawPlayers = () => {
    const pieceSize = vt(0.7);
    return Object.entries(gameState.players).map(([playerId, playerState]) => {
      const space = gameData.space[playerState.at];
      const { off_w, off_h } = orient_to_player_offset(space.orient);
      const centerX = vt(space.x + off_w);
      const centerY = vt(space.y + off_h);
      const rotated = is_player_rotated(space.orient);

      const halfPiece = vtNum(0.35);
      const imageX = `calc(${centerX} - ${halfPiece}%)`;
      const imageY = `calc(${centerY} - ${halfPiece}%)`;

      if (rotated) {
        // Use a <g> wrapper with CSS transform for rotation
        return (
          <g
            key={`player-${playerId}`}
            style={{
              transform: `rotate(90deg)`,
              transformOrigin: `${centerX} ${centerY}`,
            }}
          >
            <image
              x={imageX}
              y={imageY}
              width={pieceSize}
              height={pieceSize}
              href={`/assets/players/${playerId}.png`}
            />
          </g>
        );
      }

      return (
        <image
          key={`player-${playerId}`}
          x={imageX}
          y={imageY}
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

  const drawMessages = () => {
    if (!message) return null;

    const centerX = vt(vt_max / 2);
    const centerY = vt(3);
    const lines = message.split('\n');
    const messageFontSize = `calc(${fontSize} * 1.2)`;
    const lineSpacing = `${vtNum(0.35) * 1.3}%`;

    return (
      <text
        x={centerX}
        y={centerY}
        textAnchor="middle"
        fontSize={messageFontSize}
        fill="white"
        fontFamily="Bahnschrift, Arial, sans-serif"
      >
        {lines.map((line, i) => (
          <tspan key={i} x={centerX} dy={i === 0 ? 0 : lineSpacing}>
            {line}
          </tspan>
        ))}
      </text>
    );
  };

  const drawMovementLines = () => {
    return movementLines?.map((line, index) => {
      const fromPos = gameData.space[line.from];
      const toPos = gameData.space[line.to];

      if (!fromPos) {
        console.error('Position not found for "from":', line.from);
        return null;
      }
      if (!toPos) {
        console.error('Position not found for "to":', line.to);
        return null;
      }

      const { off_w: fromOffW, off_h: fromOffH } = orient_to_player_offset(fromPos.orient);
      const { off_w: toOffW, off_h: toOffH } = orient_to_player_offset(toPos.orient);

      const x1 = vt(fromPos.x + fromOffW);
      const y1 = vt(fromPos.y + fromOffH);
      const x2 = vt(toPos.x + toOffW);
      const y2 = vt(toPos.y + toOffH);

      return (
        <line
          key={`${line.from}-${line.to}-${index}`}
          x1={x1}
          y1={y1}
          x2={x2}
          y2={y2}
          stroke="black"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.8"
          markerEnd={line.isLast ? 'url(#arrowhead)' : undefined}
        />
      );
    })
  }

  return (
    <div className='h-full aspect-square'>
      <svg
        width="100%"
        height="100%"
      >
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
          <marker
            id="arrowhead"
            markerWidth="5"
            markerHeight="5"
            refX="4"
            refY="2.5"
            orient="auto"
          >
            <polygon
              points="0 0, 5 2.5, 0 5"
              fill="black"
            />
          </marker>
        </defs>

        <rect x="0" y="0" width="100%" height="100%" fill="#479777" stroke={border} strokeWidth="1" />
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
        {drawMovementLines()}
        {drawMessages()}
      </svg>
    </div>
  );
};

export default Board;
