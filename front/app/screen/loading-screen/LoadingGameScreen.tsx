import { useEffect } from "react";
import { fetchBackend } from "@/app/utils/api";
import { GameState, GameData } from "@/app/model/game";

// ----------------------------------------------------------------------------

interface LoadingGameScreenProps {
  onSuccess: () => void;
  onFailure: () => void;
  setGameState: (_: GameState) => void;
  setGameData: (_: GameData) => void;
  version: string;
  players: string[];
}

// ----------------------------------------------------------------------------

interface InitGameResponse {
  game_state: GameState;
  game_data: GameData;
}
function getApiFunction(props: LoadingGameScreenProps) {
  const { onSuccess, onFailure, players, setGameState, setGameData, version } = props;
  return async () => {
    try {
      const request = {
        players: players, version: version
      };
      const response = await fetchBackend(request, '/initial_game_state');
      if (!response.ok) onFailure();
      const data: InitGameResponse = await response.json();
      setGameState(data.game_state);
      setGameData(data.game_data);
      onSuccess();
    }
    catch (error) { onFailure(); }
  };
}

// ----------------------------------------------------------------------------

export default function LoadingGameScreen(props: LoadingGameScreenProps) {
  const api = getApiFunction(props);
  useEffect(() => { api(); }, [props]);
  return (
    <div className="w-screen h-screen flex flex-col">
      <div className="w-full text-center text-[5vh] mt-[5vh] mb-[5vh]">Đang tải dữ liệu game...</div>
    </div>
  );
}

// ----------------------------------------------------------------------------
