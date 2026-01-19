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
          onContinue={() => setCurrentScreen('game')}
          onBack={() => setCurrentScreen('chooseColors')}
        />
      );
    case 'game':
      return (
        <div className='game-board'>
         <GameScreen
          selectedColors={selectedColors}
          selectedCamera={selectedCamera}
          onBack={() => setCurrentScreen('checkCamera')}
        />


        </div>
      );
    default:
      return <WelcomeScreen onStart={() => setCurrentScreen('chooseColors')} />;
  }
}
