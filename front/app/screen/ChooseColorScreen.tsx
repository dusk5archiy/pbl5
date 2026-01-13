'use client';

import { Dispatch, SetStateAction } from 'react';
import { ColorType } from '@/app/utils/ColorType';

const COLORS: ColorType[] = [
  { id: 'red', name: 'Đỏ', bgClass: 'bg-red-500', borderClass: 'border-red-500' },
  { id: 'orange', name: 'Cam', bgClass: 'bg-orange-500', borderClass: 'border-orange-500' },
  { id: 'yellow', name: 'Vàng', bgClass: 'bg-yellow-400', borderClass: 'border-yellow-400' },
  { id: 'green', name: 'Lục', bgClass: 'bg-green-500', borderClass: 'border-green-500' },
  { id: 'blue', name: 'Lam', bgClass: 'bg-blue-500', borderClass: 'border-blue-500' },
  { id: 'purple', name: 'Tím', bgClass: 'bg-purple-500', borderClass: 'border-purple-500' },
];

interface SequenceDisplayProps {
  selectedColors: ColorType[];
  onReset: () => void;
}

function SequenceDisplay({ selectedColors, onReset }: SequenceDisplayProps) {
  return (
    <div className="flex items-center gap-4 p-2 rounded h-[30vh]">
      <div className="flex items-center gap-2">
        <button
          onClick={onReset}
          className="px-2 py-2 border-2 border-gray-400 rounded flex items-center justify-center active:bg-gray-300 text-sm"
        >
          Đặt lại ↺
        </button>
      </div>
      <div className="flex items-center gap-2 flex-1 bg-gray-100 px-[2vw] py-[7vh] rounded h-[20vh]">
        {selectedColors.length > 0 ? (
          selectedColors.map((color, index) => (
            <div key={index} className="flex items-center gap-2 h-full">
              <div className={`h-full aspect-square ${color.bgClass} border-4 border-black rounded`}></div>
              {index < selectedColors.length - 1 && <span className="text-2xl">→</span>}
            </div>
          ))
        ) : (
          <div className="text-gray-400 italic">Chưa chọn màu nào</div>
        )}
      </div>
    </div>
  );
}

interface ColorSelectionProps {
  selectedColors: ColorType[];
  onColorClick: (color: ColorType) => void;
  onContinue: () => void;
}

function ColorSelection({ selectedColors, onColorClick, onContinue }: ColorSelectionProps) {
  return (
    <>
      <div className="text-sm italic text-gray-600 mb-[2vh]">
        Lần lượt nhấn vào các màu theo thứ tự mong muốn.
      </div>
      <div className="flex gap-4 items-center justify-between">
        {COLORS.map((color) => (
          <button
            key={color.id}
            onClick={() => onColorClick(color)}
            disabled={selectedColors.find(c => c.id === color.id) !== undefined}
            className={`flex flex-col items-center gap-2 ${selectedColors.find(c => c.id === color.id) ? 'opacity-40 cursor-not-allowed' : ''
              }`}
          >
            <div className={`h-10 aspect-square ${color.bgClass} border-4 border-black rounded`}></div>
            <span className="text-sm font-semibold">{color.name}</span>
          </button>
        ))}
        <button
          onClick={onContinue}
          disabled={selectedColors.length <= 1}
          className={`px-4 py-2 border-4 border-green-600 rounded-lg font-bold ${selectedColors.length > 1
            ? 'bg-green-100 hover:bg-green-200 cursor-pointer'
            : 'bg-gray-100 opacity-50 cursor-not-allowed'
            }`}
        >
          Tiếp tục
        </button>
      </div>
    </>
  );
}

interface ChooseColorScreenProps {
  selectedColors: ColorType[],
  setSelectedColors: Dispatch<SetStateAction<ColorType[]>>,
  onContinue: (selectedColors: ColorType[]) => void;
  onBack: () => void;
}

export default function ChooseColorScreen({ onContinue, onBack, selectedColors, setSelectedColors }: ChooseColorScreenProps) {
  const handleColorClick = (color: ColorType) => {
    if (!selectedColors.find(c => c.id === color.id)) {
      setSelectedColors([...selectedColors, color]);
    }
  };

  const handleReset = () => {
    setSelectedColors([]);
  };

  const handleContinue = () => {
    if (selectedColors.length > 1) {
      onContinue(selectedColors);
    }
  };

  return (
    <div className="flex flex-col gap-4 h-screen bg-gray-100">
      <div className="flex flex-col m-4 grow gap-6">
        <div className="border-4 border-green-500 h-full rounded px-[4vw] py-[6vh] bg-white">
          <div className="flex items-center gap-4 h-[10vh]">
            <button
              onClick={onBack}
              className="aspect-square h-full text-2xl font-bold text-gray-600 hover:text-gray-800 rounded hover:bg-gray-100 bg-blue-200"
            >
              ↩
            </button>
            <h2 className="font-bold">Chọn màu & thứ tự chơi</h2>
          </div>
          <SequenceDisplay selectedColors={selectedColors} onReset={handleReset} />
          <ColorSelection selectedColors={selectedColors} onColorClick={handleColorClick} onContinue={handleContinue} />
        </div>
      </div>
    </div>
  );
}
