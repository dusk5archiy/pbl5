'use client'

import ChooseColorScreen from "./screen/choose-color-screen/ChooseColorScreen";
import { GameScreen } from "@/app/screen/game-screen/GameScreen";
import HomeScreen from "./screen/home-screen/HomeScreen";
import { useState } from 'react';
import LoadingGameScreen from "./screen/loading-screen/LoadingGameScreen";
import FailureScreen from "./screen/failure-screen/FailureScreen";
import { GameData, GameState } from "./model/game";
import CheckCameraScreen from "./screen/check-camera-screen/CheckCameraScreen";

export default function Home() {
  const [getCurrentScreen, setCurrentScreen] = useState<string>("home-screen");
  const [getSelectedColors, setSelectedColors] = useState<string[]>([]);
  const [gameData, setGameData] = useState<GameData | null>(null);
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [updating, setUpdating] = useState<boolean>(false);
  const [version, setVersion] = useState<string>("1");
  const [diceDetection, setDiceDetection] = useState<boolean>(false);
  const [selectedCamera, setSelectedCamera] = useState<string>("");

  switch (getCurrentScreen) {
    case 'home-screen':
      return (<HomeScreen onStart={() => setCurrentScreen('choose-color-screen')} />);
    case 'choose-color-screen':
      return (<ChooseColorScreen {...{
        onBack: () => setCurrentScreen('home-screen'),
        onNext: () => {
          if (diceDetection) {
            setCurrentScreen('check-camera-screen');
          } else {
            setCurrentScreen('loading-game-screen');
          }
        },
        getSelectedColors,
        setSelectedColors,
        version, setVersion,
        diceDetection, setDiceDetection
      }} />);
    case 'loading-game-screen':
      return (<LoadingGameScreen
        onSuccess={() => setCurrentScreen('game-screen')}
        onFailure={() => setCurrentScreen('failure-screen')}
        setGameState={setGameState}
        setGameData={setGameData}
        version={version}
        players={getSelectedColors}
      />);
    case 'check-camera-screen':
      return (
        <CheckCameraScreen {
          ...{
            onBack: () => setCurrentScreen('choose-color-screen'),
            onNext: () => setCurrentScreen('loading-game-screen'),
            selectedCamera, setSelectedCamera
          }
        } />
      );
    case 'game-screen':
      return (gameData !== null && gameState !== null &&
        <GameScreen
          gameData={gameData}
          gameState={gameState}
          setGameState={setGameState}
          onBack={() => setCurrentScreen('home-screen')}
          onError={() => { setCurrentScreen("failure-screen"); }}
          updating={updating}
          setUpdating={setUpdating}
          selectedCamera={selectedCamera}
          diceDetection={diceDetection}
        />
      );

    case 'failure-screen':
      return (<FailureScreen />)

    default:
      return undefined;
  }
}
