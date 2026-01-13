'use client';

import { useState } from 'react';
import WelcomeScreen from '@/app/screen/WelcomeScreen';
import ChooseColorScreen from '@/app/screen/ChooseColorScreen';

type Screen = 'welcome' | 'chooseColors';

export default function Home() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('welcome');

  switch (currentScreen) {
    case 'welcome':
      return <WelcomeScreen onStart={() => setCurrentScreen('chooseColors')} />;
    case 'chooseColors':
      return (
        <ChooseColorScreen
          onContinue={(colors) => {
            alert('Bắt đầu trò chơi với thứ tự: ' + colors.map(c => c.name).join(' → '));
            // TODO: Transition to game screen when implemented
          }}
          onBack={() => setCurrentScreen('welcome')}
        />
      );
    default:
      return <WelcomeScreen onStart={() => setCurrentScreen('chooseColors')} />;
  }
}
