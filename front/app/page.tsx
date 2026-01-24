'use client';

import { useState } from 'react';
import WelcomeScreen from '@/app/screen/WelcomeScreen';
import ChooseColorScreen from '@/app/screen/ChooseColorScreen';
import CheckCameraScreen from '@/app/screen/CheckCameraScreen';
import GameDataLoadingScreen from '@/app/screen/GameDataLoadingScreen';
import GameScreen from '@/app/screen/GameScreen';
import { ColorType } from '@/app/utils/ColorType';
import { GameData, GameState } from '@/app/game/model';

type Screen = 'welcome' | 'chooseColors' | 'checkCamera' | 'gameDataLoading' | 'game';

export default function Home() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('welcome');
  const [selectedColors, setSelectedColors] = useState<ColorType[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<string>('');
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [gameData, setGameData] = useState<GameData | null>(null);

  const handleGameDataLoaded = (loadedGameData: GameData, loadedGameState: GameState) => {
    setGameData(loadedGameData);
    setGameState(loadedGameState);
    setCurrentScreen('game');
  };

  switch (currentScreen) {
    case 'welcome':
      return <WelcomeScreen onStart={() => setCurrentScreen('chooseColors')} />;
    case 'chooseColors':
      return (
        <ChooseColorScreen
          selectedColors={selectedColors}
          setSelectedColors={setSelectedColors}
          onContinue={(colors) => {
            setSelectedColors(colors);
            setCurrentScreen('checkCamera');
          }}
          onBack={() => setCurrentScreen('welcome')}
        />
      );
    case 'checkCamera':
      return (
        <CheckCameraScreen
          selectedCamera={selectedCamera}
          setSelectedCamera={setSelectedCamera}
          onContinue={() => setCurrentScreen('gameDataLoading')}
          onBack={() => setCurrentScreen('chooseColors')}
        />
      );
    case 'gameDataLoading':
      return (
        <GameDataLoadingScreen
          selectedColors={selectedColors}
          onSuccess={handleGameDataLoaded}
          onBack={() => setCurrentScreen('checkCamera')}
        />
      );
    case 'game':
      return gameData && gameState && (
        <GameScreen
          selectedCamera={selectedCamera}
          gameState={gameState}
          gameData={gameData}
          onBack={() => setCurrentScreen('checkCamera')}
          onGameStateUpdate={setGameState}
        />
      );
    default:
      return <WelcomeScreen onStart={() => setCurrentScreen('chooseColors')} />;
  }
}
