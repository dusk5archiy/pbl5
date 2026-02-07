import { GameBoardProps } from "./props";
import { BOARD_BG_COLOR } from "@/app/utils/pallete";
import {
  BORDER_COLOR,
  getDrawSpaceFunction,
  getDrawBDSBannerFunction,
  getDrawBDSLabelFunction,
  getDrawRDecoration,
  getDrawUDecorationFunction,
  getDrawBDAUFunction,
  getDrawPlayersFunction,
  getDrawOTFunction,
  getDrawCircleFunction,
  getDrawTrackBorderFunction,
  getDrawActionSpaceFunction,
  getDrawMovementLinesFunction,
  getDrawActionLabelFunction,
  getDrawActionSpecialLabelFunction,
  getDrawSpaceTouchFunction as getDrawSpaceTouchFunction,
  getDrawMiddleContainerFunction
} from "./funcs";



// ----------------------------------------------------------------------------

export function GameBoard(props: GameBoardProps) {
  const { getBoardNum, gameData } = props;
  const drawSpace = getDrawSpaceFunction(props);
  const drawBDSBanner = getDrawBDSBannerFunction(props);
  const drawBDSLabel = getDrawBDSLabelFunction(props);
  const drawRDecoration = getDrawRDecoration(props);
  const drawUDecoration = getDrawUDecorationFunction(props);
  const drawBDAU = getDrawBDAUFunction(props);
  const drawOT = getDrawOTFunction(props);
  const drawPlayers = getDrawPlayersFunction(props);
  const drawCircle = getDrawCircleFunction(props);
  const drawTrackBorder = getDrawTrackBorderFunction(props);
  const drawActionSpace = getDrawActionSpaceFunction(props);
  const drawMovementLines = getDrawMovementLinesFunction(props);
  const drawActionLabel = getDrawActionLabelFunction(props);
  const drawActionSpecialLabel = getDrawActionSpecialLabelFunction(props);
  const drawSpaceTouch = getDrawSpaceTouchFunction(props);
  const drawMiddleContainer = getDrawMiddleContainerFunction(props);
  return (
    <svg
      width="100%"
      height="100%"
    >
      <defs>
        <pattern id="warning" patternUnits="userSpaceOnUse" width="4" height="4">
          <path d="M-1,1 l2,-2 M0,4 l4,-4 M3,5 l2,-2" stroke="rgba(255,255,255,0.3)" strokeWidth="2" />
        </pattern>
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
      <rect x="0" y="0" width="100%" height="100%" fill={BOARD_BG_COLOR} stroke={BORDER_COLOR} strokeWidth="1" />
      {gameData.space_id_list[getBoardNum].map(drawSpace)}
      {drawBDSBanner()}
      {drawActionSpace()}
      {drawTrackBorder()}
      {drawRDecoration()}
      {drawUDecoration()}
      {drawBDSLabel()}
      {drawBDAU()}
      {drawOT()}
      {drawActionLabel()}
      {drawActionSpecialLabel()}
      {drawPlayers()}
      {drawCircle()}
      {drawMovementLines()}
      {gameData.space_id_list[getBoardNum].map(drawSpaceTouch)}
      {drawMiddleContainer()}
    </svg>
  );
}
