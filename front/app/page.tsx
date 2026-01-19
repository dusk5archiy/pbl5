'use client';

import { useState } from 'react';
import WelcomeScreen from '@/app/screen/WelcomeScreen';
import ChooseColorScreen from '@/app/screen/ChooseColorScreen';
import CheckCameraScreen from '@/app/screen/CheckCameraScreen';
import GameScreen from '@/app/screen/GameScreen';
import { ColorType } from '@/app/utils/ColorType';

type Screen = 'welcome' | 'chooseColors' | 'checkCamera' | 'game';

export default function Home() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('welcome');
  const [selectedColors, setSelectedColors] = useState<ColorType[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<string>('');
  const [gameState, setGameState] = useState<any>(null);

  const initGame = async (colors: ColorType[]) => {
    try {
      const playerOrder = {
        players: colors.map(color => color.id)
      };
      
      const response = await fetch('http://localhost:8001/init_game', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(playerOrder),
      });
      
      const data = await response.json();
      console.log('Game initialized:', data.game_state);
      setGameState(data.game_state);
    } catch (error) {
      console.error('Error initializing game:', error);
    }
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
          onContinue={async () => {
            await initGame(selectedColors);
            setCurrentScreen('game');
          }}
          onBack={() => setCurrentScreen('chooseColors')}
        />
      );
    case 'game':
      return (
        <div className='game-board'>
         <GameScreen
          selectedCamera={selectedCamera}
          gameState={gameState}
          onBack={() => setCurrentScreen('checkCamera')}
        />


        </div>
      );
    default:
      return <WelcomeScreen onStart={() => setCurrentScreen('chooseColors')} />;
  }
}
