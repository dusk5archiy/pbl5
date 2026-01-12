'use client';

import { useState } from 'react';

type ColorType = {
  id: string;
  name: string;
  bgClass: string;
  borderClass: string;
};

const COLORS: ColorType[] = [
  { id: 'red', name: 'Đỏ', bgClass: 'bg-red-500', borderClass: 'border-red-500' },
  { id: 'orange', name: 'Cam', bgClass: 'bg-orange-500', borderClass: 'border-orange-500' },
  { id: 'yellow', name: 'Vàng', bgClass: 'bg-yellow-400', borderClass: 'border-yellow-400' },
  { id: 'green', name: 'Lục', bgClass: 'bg-green-500', borderClass: 'border-green-500' },
  { id: 'blue', name: 'Lam', bgClass: 'bg-blue-500', borderClass: 'border-blue-500' },
  { id: 'purple', name: 'Tím', bgClass: 'bg-purple-500', borderClass: 'border-purple-500' },
];

export default function Home() {
  const [gameStarted, setGameStarted] = useState(false);
  const [selectedColors, setSelectedColors] = useState<ColorType[]>([]);

  const handleColorClick = (color: ColorType) => {
    if (!selectedColors.find(c => c.id === color.id)) {
      setSelectedColors([...selectedColors, color]);
    }
  };

  const handleReset = () => {
    setSelectedColors([]);
  };

  const handleContinue = () => {
    if (selectedColors.length > 0) {
      // TODO: Proceed to next step
      alert('Bắt đầu trò chơi với thứ tự: ' + selectedColors.map(c => c.name).join(' → '));
    }
  };

  if (!gameStarted) {
    return (
      <div className="flex flex-col gap-4 h-screen bg-gray-100">
        <div className="bg-green-200 p-4 font-bold">PBL5 - Dự án kĩ thuật máy tính</div>
        <div className="flex flex-col m-4 grow gap-4 items-center">
          <div className="h-[5vh]"></div>
          <div className="text-center text-2xl font-bold uppercase font-[bahnschrift]">Hệ thống nhận diện xúc xắc và hỗ trợ người chơi cờ tỷ phú</div>
          <div className="flex grow h-full w-full justify-center items-center">
            <button 
              onClick={() => setGameStarted(true)}
              className="bg-red-300 active:bg-red-400 w-fit h-fit px-8 py-4 rounded-lg text-xl uppercase font-[bahnschrift] font-bold"
            >
              Bắt đầu
            </button>
          </div>
          <div className="h-[25vh]"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 h-screen bg-gray-100">
      <div className="bg-green-200 p-4 font-bold">PBL5 - Dự án kĩ thuật máy tính</div>
      <div className="flex flex-col m-4 grow gap-6">
        <div className="border-4 border-green-500 rounded-lg p-6 bg-white">
          <h2 className="text-xl font-bold mb-4">Chọn màu & thứ tự chơi</h2>
          
          {/* Sequence Display */}
          <div className="flex items-center gap-4 mb-6 bg-gray-50 p-4 rounded">
            <div className="flex items-center gap-2">
              <span className="text-sm">Hoàn tác</span>
              <button 
                onClick={handleReset}
                className="w-8 h-8 border-2 border-gray-400 rounded flex items-center justify-center hover:bg-gray-200"
              >
                ↺
              </button>
            </div>
            <div className="flex items-center gap-2 flex-1">
              {selectedColors.length > 0 ? (
                selectedColors.map((color, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <div className={`w-16 h-16 ${color.bgClass} border-4 border-black rounded`}></div>
                    {index < selectedColors.length - 1 && <span className="text-2xl">→</span>}
                  </div>
                ))
              ) : (
                <div className="text-gray-400 italic">Chưa chọn màu nào</div>
              )}
            </div>
          </div>

          {/* Color Selection */}
          <div className="flex gap-4 items-center">
            {COLORS.map((color) => (
              <button
                key={color.id}
                onClick={() => handleColorClick(color)}
                disabled={selectedColors.find(c => c.id === color.id) !== undefined}
                className={`flex flex-col items-center gap-2 ${
                  selectedColors.find(c => c.id === color.id) ? 'opacity-40 cursor-not-allowed' : 'hover:scale-105'
                } transition-all`}
              >
                <div className={`w-20 h-20 ${color.bgClass} border-4 border-black rounded`}></div>
                <span className="text-sm font-semibold">{color.name}</span>
              </button>
            ))}
            <button
              onClick={handleContinue}
              disabled={selectedColors.length === 0}
              className={`px-6 py-3 border-4 border-green-600 rounded-lg font-bold ${
                selectedColors.length > 0 
                  ? 'bg-green-100 hover:bg-green-200 cursor-pointer' 
                  : 'bg-gray-100 opacity-50 cursor-not-allowed'
              }`}
            >
              Tiếp tục
            </button>
          </div>

          <div className="mt-6 text-sm italic text-gray-600">
            Lần lượt nhấn vào các màu theo thứ tự mong muốn.
          </div>
        </div>
      </div>
    </div>
  );
}
