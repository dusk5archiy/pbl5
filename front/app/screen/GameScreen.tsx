'use client';

import { ColorType } from '@/app/utils/ColorType';

interface GameScreenProps {
  selectedColors: ColorType[];
  onBack: () => void;
}

export default function GameScreen({ selectedColors, onBack }: GameScreenProps) {
  return (
    <button
      onClick={onBack}
      className="aspect-square h-full text-2xl font-bold text-gray-600 hover:text-gray-800 rounded hover:bg-gray-100 bg-blue-200"
    >
      ↩
    </button>
  );
}
