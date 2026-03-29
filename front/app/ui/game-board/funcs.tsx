import { GameData, Space } from "@/app/model/game";
import { GameBoardProps } from "./props";
import { formatBudget } from "@/app/utils/format";
import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { CSSProperties } from "react";

export const BORDER_COLOR = "#8B4513"
const TRACK_BORDER_WIDTH = 3;

// ----------------------------------------------------------------------------

export function getVtFunction(props: GameBoardProps) {
  const { gameData, getBoardNum } = props;
  return (x: number) => `${x / gameData.board_size[getBoardNum] * 100}%`;
}

// ----------------------------------------------------------------------------

export function getDrawSpaceFunction(props: GameBoardProps) {
  const { gameData, gameState } = props;
  const vt = getVtFunction(props);
  return (spaceId: string) => {
    let fill = "white";
    let owner = gameState.logic.bds[spaceId]?.owner || null;
    if (owner != null) {
      fill = COLOR_UI_INFO[owner].lightColorCode;
    }
    const space = gameData.space[spaceId];
    return (
      <rect
        key={spaceId}
        x={vt(space.x)}
        y={vt(space.y)}
        width={vt(space.w)}
        height={vt(space.h)}
        fill={fill}
        stroke={BORDER_COLOR}
        strokeWidth="1"
      />
    );
  }
}

// ----------------------------------------------------------------------------

export function getDrawSpaceTouchFunction(props: GameBoardProps) {
  const { gameData, focusBds, setBdsShown, gameState, tripleDiceFunc, setPropertyTab, guest } = props;
  const can_interact = guest == null || guest == gameState.logic.viewing_player;
  const vt = getVtFunction(props);
  const triple_dice_chore = gameState.current_chore.triple_dice;

  function ev(spaceId: string) {
    if (can_interact && triple_dice_chore != null) {
      tripleDiceFunc({ destination: spaceId });
      return;
    }

    if (Object.keys(gameData.bds).includes(spaceId)) {
      setBdsShown(1);
      setPropertyTab("bds");
      focusBds(spaceId);
    }
  }

  return (spaceId: string) => {
    const space = gameData.space[spaceId];
    return (
      <rect
        key={spaceId}
        x={vt(space.x)}
        y={vt(space.y)}
        onClick={() => ev(spaceId)}
        width={vt(space.w)}
        height={vt(space.h)}
        style={
          {
            "--fill-color": triple_dice_chore != null ? "#60a5fa" : "#99a1af"
          } as CSSProperties
        }
        className="fill-black opacity-0 stroke-8 hover:fill-(--fill-color) hover:opacity-50 active:opacity-70"
      />
    );
  }
}

// ----------------------------------------------------------------------------

export function getDrawBDSBannerFunction(props: GameBoardProps) {
  const { gameData, getBoardNum } = props;
  const vt = getVtFunction(props);
  const orient_to_wh = (orient: string) => {
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
  const orient_to_offset = (orient: string) => {
    switch (orient) {
      case "S":
      case "E":
        return { w: 0, h: 0 };
      case "N":
        return { w: 0, h: 1.5 };
      case "W":
      default:
        return { w: 1.5, h: 0 };
    }
  }
  return () => Object.keys(gameData.bds)
    .filter(
      (id) =>
        gameData.space_id_list[getBoardNum].includes(id) &&
        !["R", "U", "T", "SB", "CB", "MT"].includes(gameData.bds[id].group)
    ).map(
      (spaceId: string) => {
        const group = gameData.bds[spaceId].group;
        const space = gameData.space[spaceId];
        const { w, h } = orient_to_wh(space.orient);
        const { w: off_w, h: off_h } = orient_to_offset(space.orient);
        return (
          <rect key={spaceId} x={vt(space.x + off_w)} y={vt(space.y + off_h)} width={w} height={h} fill={gameData.pallete[group]} stroke={BORDER_COLOR} strokeWidth="1" />
        );
      });
}

// ----------------------------------------------------------------------------

function getDrawTextFunction(gameData: GameData, getBoardNum: number) {
  const scale = 0.35 / gameData.board_size[getBoardNum];
  const fontSize = `${scale * 50}vw`;
  return (key: string, text: string, x: string, y: string, color: string, rotate: boolean = false, fontFamily: string = "sans-serif", fontWeight: string = "normal") => {
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
}

// ----------------------------------------------------------------------------

export function getDrawLabelFunction(props: GameBoardProps) {
  const { gameData, getBoardNum } = props;
  const vt = getVtFunction(props);
  const drawText = getDrawTextFunction(gameData, getBoardNum);
  return (key: string, text: string, space: Space, color: string = "black", fontWeight: string = "normal", rotate: boolean = false) => {
    const fontFamily: string = "sans-serif";
    return drawText(key, text, vt(space.x + space.w / 2), vt(space.y + space.h / 2), color, rotate, fontFamily, fontWeight);
  };
}

// ----------------------------------------------------------------------------

export function getDrawBDSLabelFunction(props: GameBoardProps) {
  const { gameData, gameState, getBoardNum } = props;
  const drawLabel = getDrawLabelFunction(props);
  return () => Object.keys(gameData.bds)
    .filter(
      (id) =>
        gameData.space_id_list[getBoardNum].includes(id)
    ).map((spaceId: string) => {
      const space = gameData.space[spaceId];
      const price = gameData.bds[spaceId].price;
      let text = `${spaceId}\n${formatBudget(price)}`;
      let color = "black";
      let weight = "normal"
      const owner = gameState.logic.bds[spaceId].owner;
      const level = gameState.ui.bds[spaceId].level;
      if (level != null && owner != null) {
        text = `${spaceId}\nLv.${level >= 0 ? level : "-"}`;
        weight = "bold";
      }
      return drawLabel(`text-${spaceId}`, text, space, color, weight);
    });
}

// ----------------------------------------------------------------------------

export function getDrawRDecoration(props: GameBoardProps) {
  const { gameData, gameState, getBoardNum } = props;
  const vt = getVtFunction(props);
  const drawLabel = getDrawLabelFunction(props);
  const orient_to_offset_label = (orient: string) => {
    switch (orient) {
      case "S":
        return { w: 0, h: -2 };
      case "N":
        return { w: 0, h: 2 };
      case "W":
        return { w: 2, h: 0 };
      case "E":
      default:
        return { w: -2, h: 0 };
    }
  }

  function orient_to_wh(orient: string) {
    switch (orient) {
      case "S":
      case "N":
        return { w: vt(1), h: vt(4) };
      case "W":
      case "E":
      default:
        return { w: vt(4), h: vt(1) };
    }
  }
  function orient_to_wh_2(orient: string) {
    switch (orient) {
      case "S":
      case "N":
        return { w: vt(1), h: vt(2) };
      case "W":
      case "E":
      default:
        return { w: vt(2), h: vt(1) };
    }
  }
  function orient_to_offset(orient: string) {
    switch (orient) {
      case "S":
        return { w: 0, h: -2 }
      case "N":
      case "W":
        return { w: 0, h: 0 };
      case "E":
      default:
        return { w: -2, h: 0 };
    }
  }

  function orient_to_line(orient: string) {
    switch (orient) {
      case "S":
        return { x1: 0, y1: 2, x2: 2, y2: 2 };
      case "N":
        return { x1: 0, y1: 0, x2: 2, y2: 0 };
      case "W":
        return { x1: 0, y1: 0, x2: 0, y2: 1 };
      case "E":
        return { x1: 2, y1: 0, x2: 2, y2: 1 };
      default:
        return { x1: 0, y1: 0, x2: 0, y2: 0 };
    }
  }
  return () => Object.keys(gameData.bds)
    .filter(
      (id) =>
        gameData.space[id].board == getBoardNum && gameData.bds[id].group == "R"
    ).map((spaceId: string) => {
      const space = gameData.space[spaceId];
      const existA = Object.keys(gameData.space).includes(spaceId + "A");
      const { w, h } = existA ? orient_to_wh(space.orient) : orient_to_wh_2(space.orient);
      const { x1, y1, x2, y2 } = orient_to_line(space.orient);
      let fill = "white";
      let owner = gameState.logic.bds[spaceId]?.owner || null;
      if (owner != null) {
        fill = COLOR_UI_INFO[owner].lightColorCode;
      }
      if (existA) {
        const { w: off_w, h: off_h } = orient_to_offset(space.orient);
        const { w: off_w_label, h: off_h_label } = orient_to_offset_label(space.orient);
        const text = "Ga\ntàu";
        const s: Space = {
          board: space.board,
          track: space.track,
          orient: "",
          x: space.x + off_w_label,
          y: space.y + off_h_label,
          w: space.w,
          h: space.h,
        };
        return (
          <g key={`banner-${spaceId}`}>
            <rect x={vt(space.x + off_w)} y={vt(space.y + off_h)} width={w} height={h} fill={fill} stroke={BORDER_COLOR} strokeWidth="1" />
            <rect x={vt(space.x + off_w)} y={vt(space.y + off_h)} width={w} height={h} fill="url(#gray25)" stroke={BORDER_COLOR} strokeWidth="1" />
            <line x1={vt(space.x + x1)} y1={vt(space.y + y1)} x2={vt(space.x + x2)} y2={vt(space.y + y2)} stroke="grey" strokeWidth={TRACK_BORDER_WIDTH} />
            {drawLabel(`text-${spaceId}-R`, text, s)}
          </g>
        );
      }
      else {
        return (
          <g key={`banner-${spaceId}`}>
            <rect x={vt(space.x)} y={vt(space.y)} width={w} height={h} fill={fill} stroke={BORDER_COLOR} strokeWidth="1" />
            <rect x={vt(space.x)} y={vt(space.y)} width={w} height={h} fill="url(#gray25)" stroke={BORDER_COLOR} strokeWidth="1" />
            <line x1={vt(space.x + x1)} y1={vt(space.y + y1)} x2={vt(space.x + x2)} y2={vt(space.y + y2)} stroke="grey" strokeWidth={TRACK_BORDER_WIDTH} />
          </g>
        );
      }
    });
}

// ----------------------------------------------------------------------------

export function getDrawUDecorationFunction(props: GameBoardProps) {
  const { gameData, getBoardNum } = props;
  const vt = getVtFunction(props);
  const orient_to_offset = (orient: string) => {
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

  const orient_to_wh = (orient: string) => {
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


  return () => Object.keys(gameData.bds)
    .filter(
      (id) =>
        gameData.space_id_list[getBoardNum].includes(id) &&
        ["U", "T", "SB", "CB", "MT"].includes(gameData.bds[id].group)
    ).map(
      (spaceId: string) => {
        const space = gameData.space[spaceId];
        const key = `banner-${spaceId}`;
        const { off_w, off_h } = orient_to_offset(space.orient);
        const { w, h } = orient_to_wh(space.orient);
        const group = gameData.bds[spaceId].group;
        return (
          <rect key={key} x={vt(space.x + off_w)} y={vt(space.y + off_h)} width={w} height={h} fill={gameData.pallete[group]} stroke="white" strokeWidth="1" />
        );
      }
    );
}

// ----------------------------------------------------------------------------

export function getDrawBDAUFunction(props: GameBoardProps) {
  const { gameData, getBoardNum } = props;
  const drawLabel = getDrawLabelFunction(props);

  return () => {
    const spaceId = "BDAU";
    const space = gameData.space[spaceId];
    const text = "BẮT ĐẦU";
    return (
      gameData.space_id_list[getBoardNum].includes("BDAU") &&
      drawLabel(`text-${spaceId}`, text, space, gameData.pallete[spaceId])
    );
  }
}

// ----------------------------------------------------------------------------

export function getDrawActionLabelFunction(props: GameBoardProps) {
  const { gameData, getBoardNum } = props;
  const drawLabel = getDrawLabelFunction(props);

  return () => Object.entries(gameData.action_label).map(
    ([spaceId, text]) => {
      const space = gameData.space[spaceId];
      return (
        space.board == getBoardNum &&
        drawLabel(`text-${spaceId}`, text, space)
      );
    }
  );
}

// ----------------------------------------------------------------------------

export function getDrawActionSpecialLabelFunction(props: GameBoardProps) {
  const { gameData, getBoardNum } = props;
  const drawLabel = getDrawLabelFunction(props);

  return () => Object.entries(gameData.action_special_label).map(
    ([spaceId, text]) => {
      const space = gameData.special_space[spaceId];
      return (
        space.board == getBoardNum &&
        drawLabel(`text-${spaceId}`, text, space)
      );
    }
  );
}

// ----------------------------------------------------------------------------
export function getDrawOTFunction(props: GameBoardProps) {
  const { gameData, getBoardNum } = props;
  const drawLabel = getDrawLabelFunction(props);
  const vt = getVtFunction(props);

  return () => {
    const spaceId = "OT";
    const OT = gameData.special_space[spaceId];
    const TT = gameData.space["TT"];
    const tt_1: Space = { board: TT.board, track: TT.track, orient: TT.orient, x: TT.x, y: TT.y, w: (TT.w - OT.w) * 2 / 3, h: OT.h };
    const tt_2: Space = { board: TT.board, track: TT.track, orient: TT.orient, x: OT.x, y: TT.y + OT.w, w: OT.w, h: TT.h - OT.h };
    return (
      gameData.space_id_list[getBoardNum].includes("TT") &&
      <g key={`g-${spaceId}`}>
        <rect
          key={spaceId}
          x={vt(OT.x)}
          y={vt(OT.y)}
          width={vt(OT.w)}
          height={vt(OT.h)}
          fill={gameData.pallete[spaceId]}
          stroke={BORDER_COLOR}
          strokeWidth="1"
        />
        {drawLabel(`text-TT1`, "Thăm", tt_1, "black", "normal", true)}
        {drawLabel(`text-TT2`, "tù", tt_2, "black")}
      </g>
    );
  }
}

// ----------------------------------------------------------------------------
const orient_to_player_offset = (space: Space) => {
  const mid = 0.5;
  const high = 0.8;
  switch (space.orient) {
    case "S":
    case "SW":
    case "SE":
      return { off_w: mid * space.w, off_h: high * space.h };
    case "W":
      return { off_w: (1 - high) * space.w, off_h: mid * space.h };
    case "NW":
    case "NE":
    case "N":
      return { off_w: mid * space.w, off_h: (1 - high) * space.h };
    case "E":
      return { off_w: high * space.w, off_h: mid * space.h };
    default:
      return { off_w: 0, off_h: 0 };
  }
}

// ----------------------------------------------------------------------------

export function getDrawPlayersFunction(props: GameBoardProps) {
  const { gameData, getBoardNum, gameState } = props;
  const vt = getVtFunction(props);

  const is_player_rotated = (orient: string) => {
    switch (orient) {
      case "W":
      case "E":
        return true;
      default:
        return false;
    }
  }

  return () => {
    const scale = 0.7;
    const pieceSize = vt(scale);
    return Object.entries(gameState.logic.player)
      .filter(([_, info]) => gameData.space[info.at]?.board == getBoardNum || gameData.special_space[info.at]?.board == getBoardNum)
      .map(([playerId, playerState]) => {
        const space = gameData.space[playerState.at] || gameData.special_space[playerState.at];
        let { off_w, off_h } = orient_to_player_offset(space);
        const centerX = vt(space.x + off_w);
        const centerY = vt(space.y + off_h);

        const rotated = is_player_rotated(space.orient);

        const halfPiece = vt(scale / 2);
        const imageX = `calc(${centerX} - ${halfPiece})`;
        const imageY = `calc(${centerY} - ${halfPiece})`;

        return (
          <g
            key={`player-${playerId}`}
            style={rotated ? {
              transform: `rotate(90deg)`,
              transformOrigin: `${centerX} ${centerY}`,
            } : {}}
          >
            <image
              x={imageX}
              y={imageY}
              width={pieceSize}
              href={`/assets/player/${playerId}.svg`}
            />
          </g>
        );
      });
  };
}

// ----------------------------------------------------------------------------

export function getDrawCircleFunction(props: GameBoardProps) {
  const { gameState, gameData, getBoardNum } = props;
  const vt = getVtFunction(props);
  return () => {
    const playerId = gameState.logic.current_player;
    const space_id = gameState.logic.player[playerId].at;
    const space = gameData.space[space_id] || gameData.special_space[space_id];
    const { off_w, off_h } = orient_to_player_offset(space);
    return (
      (gameData.space[space_id]?.board == getBoardNum || gameData.special_space[space_id]?.board == getBoardNum) &&
      <circle
        cx={vt(space.x + off_w)}
        cy={vt(space.y + off_h)}
        r={vt(1)}
        fill="none"
        stroke={COLOR_UI_INFO[playerId].darkColorCode}
        strokeWidth="3"
      />
    );
  };

}

// ----------------------------------------------------------------------------

export function getDrawTrackBorderFunction(props: GameBoardProps) {
  const { gameData, getBoardNum } = props;
  const vt = getVtFunction(props);
  const board = gameData.track_border[getBoardNum];
  return () => board.map(
    (track_border, track_idx) => {
      const { top_left: low, bottom_right: high } = track_border;
      return (
        <g key={`track_border-${getBoardNum}-${track_idx}`}>
          <line x1={vt(low)} y1={vt(low)} x2={vt(low)} y2={vt(high)} stroke="grey" strokeWidth={TRACK_BORDER_WIDTH} />
          <line x1={vt(low)} y1={vt(high)} x2={vt(high)} y2={vt(high)} stroke="grey" strokeWidth={TRACK_BORDER_WIDTH} />
          <line x1={vt(high)} y1={vt(high)} x2={vt(high)} y2={vt(low)} stroke="grey" strokeWidth={TRACK_BORDER_WIDTH} />
          <line x1={vt(high)} y1={vt(low)} x2={vt(low)} y2={vt(low)} stroke="grey" strokeWidth={TRACK_BORDER_WIDTH} />
        </g>
      )
    }
  );
}

// ----------------------------------------------------------------------------

export function getDrawActionSpaceFunction(props: GameBoardProps) {
  const { gameData, getBoardNum } = props;
  const vt = getVtFunction(props);
  return () => Object.entries(gameData.action)
    .filter(([actionId, _]) => gameData.space_id_list[getBoardNum].includes(actionId))
    .map(([actionId, info]) => {
      const space = gameData.space[actionId];
      const group = info.group;
      return (
        <g key={`action-${actionId}`}>
          <rect x={vt(space.x)} y={vt(space.y)} width={vt(space.w)} height={vt(space.h)} fill={gameData.pallete[group]} stroke={BORDER_COLOR} strokeWidth="1" />
          <rect x={vt(space.x)} y={vt(space.y)} width={vt(space.w)} height={vt(space.h)} fill="url(#warning)" stroke={BORDER_COLOR} strokeWidth="1" />
        </g>
      );
    });
}
// ----------------------------------------------------------------------------

export function getDrawMovementLinesFunction(props: GameBoardProps) {
  const vt = getVtFunction(props);
  const { gameState, gameData, getBoardNum } = props;
  return () => gameState.effect.movement_lines
    .filter(
      ({ start, end }) => {
        const start_space = gameData.space[start];
        const end_space = gameData.space[end];
        return start_space.board == getBoardNum && end_space.board == getBoardNum;
      }
    )
    .map(
      ({ arrow, start, end }) => {
        const start_space = gameData.space[start];
        const end_space = gameData.space[end];
        const { off_w: fromOffW, off_h: fromOffH } = orient_to_player_offset(start_space);
        const { off_w: toOffW, off_h: toOffH } = orient_to_player_offset(end_space);
        const x1 = vt(start_space.x + fromOffW);
        const y1 = vt(start_space.y + fromOffH);
        const x2 = vt(end_space.x + toOffW);
        const y2 = vt(end_space.y + toOffH);
        return (
          <line
            key={`arrow-${start}-${end}`}
            x1={x1}
            y1={y1}
            x2={x2}
            y2={y2}
            stroke="black"
            strokeWidth="2"
            strokeLinecap="round"
            opacity="0.8"
            markerEnd={arrow ? 'url(#arrowhead)' : undefined}
          />);
      }
    );
}

// ----------------------------------------------------------------------------

export function getDrawMiddleContainerFunction(props: GameBoardProps) {
  const {
    gameData, getBoardNum
  } = props;
  const vt = getVtFunction(props);
  const track_border = gameData.track_border[getBoardNum][gameData.track_border[getBoardNum].length - 1];
  const { top_left: low, bottom_right: high } = track_border;
  return () =>
    <foreignObject x={vt(low + 2)} y={vt(low + 2)} width={vt(high - low - 4)} height={vt(high - low - 4)}>
    </foreignObject>
    ;
}

// ----------------------------------------------------------------------------

