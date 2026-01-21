'use client';

import { useState, useEffect } from 'react';
import { ColorType } from '@/app/utils/ColorType';
import { fetchGameData } from '@/app/game/data';
import { GameData, GameState } from '@/app/game/model';

interface GameDataLoadingScreenProps {
  selectedColors: ColorType[];
  onSuccess: (gameData: GameData, gameState: GameState) => void;
  onBack: () => void;
}

export default function GameDataLoadingScreen({
  selectedColors,
  onSuccess,
  onBack
}: GameDataLoadingScreenProps) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentStep, setCurrentStep] = useState<string>('');

  useEffect(() => {
    const loadAllData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Step 1: Load static game data
        setCurrentStep('Đang tải dữ liệu game tĩnh...');
        const gameData = await fetchGameData();

        // Step 2: Initialize game with selected colors
        setCurrentStep('Đang khởi tạo game...');
        const playerOrder = {
          players: selectedColors.map(color => color.id)
        };

        const response = await fetch('http://localhost:8001/init_game', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(playerOrder),
        });

        if (!response.ok) {
          throw new Error(`Failed to initialize game: ${response.statusText}`);
        }

        const initData = await response.json();
        const gameState = initData.game_state;

        // Success - pass both data objects
        onSuccess(gameData, gameState);

      } catch (err) {
        setError(err instanceof Error ? err.message : 'Đã xảy ra lỗi không xác định');
      } finally {
        setLoading(false);
      }
    };

    loadAllData();
  }, [selectedColors, onSuccess]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
        <div className="text-center space-y-4">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto"></div>
          <div className="text-xl font-semibold">
            {currentStep || 'Đang tải...'}
          </div>
          <div className="text-gray-400">
            Vui lòng đợi trong giây lát
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white">
        <div className="text-center space-y-6 max-w-md mx-auto px-4">
          <div className="text-red-400 text-6xl">⚠️</div>
          <div>
            <h2 className="text-2xl font-bold text-red-400 mb-2">
              Lỗi tải dữ liệu
            </h2>
            <p className="text-gray-300">
              {error}
            </p>
          </div>
          <button
            onClick={onBack}
            className="px-6 py-3 bg-red-600 text-white text-lg font-bold rounded hover:bg-red-700 transition-colors"
          >
            Quay lại
          </button>
        </div>
      </div>
    );
  }

  // This should not be reached, but just in case
  return null;
}
