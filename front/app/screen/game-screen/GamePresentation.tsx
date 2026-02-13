'use client'

import { useEffect, useRef, useState } from "react";
import { GameScreenProps, } from "./props";
import { GameBoard } from "@/app/ui/game-board/GameBoard";
import {
  GameBoardProps,
  IActionCardSelectorsProps,
  IApiProps,
  IGameDataStateProps,
  IGameSettingsProps,
  IPropertySelectorsProps,
  IDiceDetectionProps,
  IDiceDetectionResult,
  IDice,
  ISendDataProps
} from "@/app/ui/game-board/props";
import { HandPanel } from "@/app/ui/game-board/HandPanel";
import {
  getNumFunction,
  getAuctionFunction,
  getBdsFunction,
  getDestinationFunction,
  getUseActionCardFunction,
  getTradeFunction,
  getDiceNumFunction,
  getRollDiceFunction,
  getNormalFunction,
} from "./funcs";
import { LeftPanel } from "@/app/ui/game-board/LeftPanel";
import { PromptModal } from "@/app/ui/game-board/PromptModal";
import { DiceConfirmTab } from "@/app/ui/game-board/DiceConfirmTab";
import { WS_BACKEND_PREFIX } from "@/app/utils/env";

// ----------------------------------------------------------------------------

export function GamePresentation(props: GameScreenProps) {
  const { onBack, gameData, gameState, setGameState, selectedCamera, diceDetection } = props;

  const [bdsShown, setBdsShown] = useState<number>(0);
  const [propertyTab, setPropertyTab] = useState<number>(0);
  const [boardShown, setBoardShown] = useState<boolean>(true);


  // Default values for selectors
  function getDefault() {
    const bds_id = Object.keys(gameData.bds)[0];
    const { group } = gameData.bds[bds_id];
    const { board, track } = gameData.space[bds_id];

    const action_group = Object.keys(gameState.logic.action)[0];
    const action_card = Object.keys(gameState.logic.action[action_group])[0];

    return {
      default_board: board,
      default_track: track,
      default_group: group,
      default_bds: bds_id,
      default_action_group: action_group,
      default_action_card: action_card
    };
  }

  const {
    default_board,
    default_track,
    default_group,
    default_bds,
    default_action_group,
    default_action_card,
  } = getDefault();

  // Board selector
  const [getBoardNum, setBoardNum] = useState<number>(0);

  // Property Selectors
  const [selectedBoard, setSelectedBoard] = useState<number>(default_board);
  const [selectedTrack, setSelectedTrack] = useState<number>(default_track);
  const [selectedGroup, setSelectedGroup] = useState<string>(default_group);
  const [selectedBds, setSelectedBds] = useState<string>(default_bds);

  // Action card selectors
  const [selectedActionGroup, setSelectedActionGroup] = useState<string>(default_action_group);
  const [selectedActionCard, setSelectedActionCard] = useState<string>(default_action_card);

  // Automatically selects the board, track and group of a property when it is focused
  const focusBds = (bds_id: string) => {
    const space = gameData.space[bds_id];
    const bds = gameData.bds[bds_id];
    setSelectedBoard(space.board);
    setSelectedTrack(space.track);
    setSelectedGroup(bds.group);
    setSelectedBds(bds_id);
  }

  // Dice detection results
  const [diceDetectionResult, setDiceDetectionResult] = useState<IDiceDetectionResult | null>(null);
  const [encodedImage, setEncodedImage] = useState<string | null>(null);

  // Effects from the game state
  useEffect(() => {
    const board = gameState.effect.board;
    if (board != null) {
      setBoardNum(board);
      setBdsShown(0);
    }

    const select_bds = gameState.effect.select_bds;
    if (select_bds != null) {
      focusBds(select_bds);
    }

    if (diceDetection) {
      if (diceDetectionResult != null) {
        setEncodedImage(null);
        setDiceDetectionResult(null);
      }
    }

  }, [gameState]);

  // Video refs states
  const videoRef = useRef<HTMLVideoElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);

  // WebSocket connection
  const [ws, setWs] = useState<WebSocket | null>(null);

  // WebSocket connection
  useEffect(() => {
    const websocket = new WebSocket(WS_BACKEND_PREFIX + '/ws/game_states');
    websocket.onopen = () => {
      setWs(websocket);
    };
    websocket.onmessage = (event) => {
      const game_state = JSON.parse(event.data);
      setGameState(game_state);
    };
    websocket.onclose = () => { };
    return () => {
      websocket.close();
    };
  }, []);

  if (ws == null) {
    return null;
  }

  // Api's
  const rollDiceFunc = getRollDiceFunction(props, "roll_dice", ws);
  const endTurnFunc = getNormalFunction(props, "end_turn", ws);
  const buyFunc = getNumFunction(props, "buy", ws);
  const payFunc = getNumFunction(props, "pay", ws);
  const receiveMortgageFunc = getNumFunction(props, "receive_mortgage", ws);
  const auctionFunc = getAuctionFunction(props, "auction", ws);
  const upgradeBdsFunc = getBdsFunction(props, "upgrade_bds", ws);
  const downgradeBdsFunc = getBdsFunction(props, "downgrade_bds", ws);
  const mortgageBdsFunc = getBdsFunction(props, "mortgage_bds", ws);
  const unmortgageBdsFunc = getBdsFunction(props, "unmortgage_bds", ws);
  const diceCFunc = getNormalFunction(props, "dice_c", ws);
  const diceXbFunc = getNormalFunction(props, "dice_xb", ws);
  const actionCardFunc = getNormalFunction(props, "action_card", ws);
  const tripleDiceFunc = getDestinationFunction(props, "triple_dice", ws);
  const jailFunc = getDiceNumFunction(props, "jail", ws);
  const twoDiceRentUFunc = getRollDiceFunction(props, "two_dice_rent_u", ws);
  const useActionCardFunc = getUseActionCardFunction(props, "use_action_card", ws);
  const startTradeFunc = getNormalFunction(props, "start_trade", ws);
  const tradeFunc = getTradeFunction(props, "trade", ws);

  // Send roll dice data
  const sendRollDice = ({ dice_1, dice_2 }: IDice) => {
    const jail_chore = gameState.current_chore.jail;
    const roll_dice_chore = gameState.current_chore.roll_dice;
    const two_dice_rent_u_chore = gameState.current_chore.two_dice_rent_u;
    if (jail_chore != null) { jailFunc({ response: 0, dice_1, dice_2 }) }
    if (roll_dice_chore != null) { rollDiceFunc({ dice_1, dice_2 }) }
    if (two_dice_rent_u_chore != null) { twoDiceRentUFunc({ dice_1, dice_2 }) }
  };

  // Dice detection
  const getDiceCaptureResults = async () => {
    if (!videoRef?.current) return;
    const canvas = document.createElement('canvas');
    const context = canvas.getContext('2d');
    if (!context) return;
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    context.drawImage(videoRef.current, 0, 0);
    canvas.toBlob(
      async (blob) => {
        if (!blob) return;
        const formData = new FormData();
        formData.append("file", blob, "capture.jpg");
        try {
          const response = await fetch("http://192.168.137.1:8000/detect", { method: 'POST', body: formData });
          const data = await response.json();
          setDiceDetectionResult(data);
          setEncodedImage(canvas.toDataURL());
        } catch (e) {
          console.log(e);
        }
      },
      'image/jpeg', 0.8);
  }


  const api_props: IApiProps = {
    rollDiceFunc,
    endTurnFunc,
    buyFunc,
    payFunc,
    receiveMortgageFunc,
    auctionFunc,
    upgradeBdsFunc,
    downgradeBdsFunc,
    mortgageBdsFunc,
    unmortgageBdsFunc,
    diceCFunc,
    diceXbFunc,
    actionCardFunc,
    tripleDiceFunc,
    jailFunc,
    twoDiceRentUFunc,
    useActionCardFunc,
    startTradeFunc,
    tradeFunc,
  };

  const video_ref_props: IDiceDetectionProps = {
    selectedCamera,
    videoRef,
    stream,
    setStream,
    getDiceCaptureResults,
    diceDetectionResult,
    setDiceDetectionResult,
    encodedImage,
    setEncodedImage,
  };

  const game_settings_props: IGameSettingsProps = {
    selectedCamera,
    diceDetection
  };

  const game_data_state_props: IGameDataStateProps = {
    gameState, gameData,
  };

  const property_selector_props: IPropertySelectorsProps = {
    selectedBoard, setSelectedBoard,
    selectedTrack, setSelectedTrack,
    selectedGroup, setSelectedGroup,
    selectedBds, setSelectedBds,
    focusBds,
  };

  const action_card_selector_props: IActionCardSelectorsProps = {
    selectedActionGroup, setSelectedActionGroup,
    selectedActionCard, setSelectedActionCard,
  };

  const send_data_props: ISendDataProps = {
    sendRollDice
  };

  const game_board_props: GameBoardProps = {
    ...send_data_props,
    ...api_props,
    ...video_ref_props,
    ...game_settings_props,
    ...game_data_state_props,
    ...property_selector_props,
    ...action_card_selector_props,
    getBoardNum,
    bdsShown, setBdsShown,
    propertyTab, setPropertyTab,
    tripleDiceFunc,
  };

  return (
    <div className="@container w-screen h-screen px-[2vw] py-[2vh] flex gap-[2vh] bg-[#2E6C3D] overflow-hidden">
      {
        diceDetectionResult != null ?
          <DiceConfirmTab {...game_board_props} /> :
          bdsShown == 0 ?
            <>
              <div className={`w-[calc(100%-95cqh)] h-full flex flex-col gap-[2vh]`}>
                <div className="w-full h-full flex flex-col gap-[1vh] overflow-y-scroll">
                  {
                    boardShown && <div className="w-full min-h-[50%] flex">
                      <PromptModal {...game_board_props} />
                    </div>
                  }
                  <div className={`"w-full ${boardShown ? "min-h-[49%]" : "min-h-full"} flex"`}>
                    <LeftPanel {...game_board_props} />
                  </div>
                  <div className="w-full h-[10%] flex gap-[0.5vw]">
                    <button
                      onClick={onBack}
                      className="w-max h-max px-[2vw] py-[2vh] text-[1.5vw] font-bold text-gray-600 rounded bg-blue-200 active:bg-blue-400"
                    >Trở về
                    </button>
                    <button
                      onClick={() => setBoardNum((getBoardNum + 1) % gameData.board_size.length)}
                      className="w-max h-max px-[2vw] py-[2vh] text-[1.5vw] font-bold text-gray-600 rounded bg-emerald-200 active:bg-emerald-400"
                    >Đổi bàn
                    </button>
                    <button
                      onClick={() => setBoardShown(!boardShown)}
                      className="w-max h-max px-[2vw] py-[2vh] text-[1.5vw] font-bold text-gray-600 rounded bg-rose-200 active:bg-rose-400"
                    >{!boardShown ? "Hiện bàn" : "Ẩn bàn"}
                    </button>
                    {
                      gameState.turns != null &&
                      <div
                        className="w-max h-max px-[2vw] py-[2vh] text-[1.5vw] rounded text-white border-2 border-white"
                      >{gameState.turns}
                      </div>
                    }
                  </div>
                </div>
              </div>
              <div className="w-[95cqh] h-[95cqh]">
                {
                  boardShown ? <div style={{
                    width: "100%",
                    height: "100%",
                    aspectRatio: "1 / 1"
                  }}>
                    <GameBoard {...game_board_props} /> :
                  </div>
                    :
                    <PromptModal {...game_board_props} />
                }
              </div>
            </>
            :
            <HandPanel {...game_board_props} />
      }
    </div>
  );
}
