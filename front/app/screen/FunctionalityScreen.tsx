'use client';

interface FunctionalityScreenProps {
  onBack: () => void;
  onExit: () => void;
  onDevRoll: (dice1: number, dice2: number) => void;
  activeTab: 'main' | 'dev';
  setActiveTab: (tab: 'main' | 'dev') => void;
  devDice1: number;
  setDevDice1: (value: number) => void;
  devDice2: number;
  setDevDice2: (value: number) => void;
  canRoll: boolean;
}

export default function FunctionalityScreen({ 
  onBack, 
  onExit, 
  onDevRoll,
  activeTab,
  setActiveTab,
  devDice1,
  setDevDice1,
  devDice2,
  setDevDice2,
  canRoll
}: FunctionalityScreenProps) {
  const cycleDice = (current: number) => (current % 6) + 1;

  const handleDevRoll = () => {
    onDevRoll(devDice1, devDice2);
  };

  return (
    <div className="flex flex-col h-screen bg-[#2E6C3D]">
      <div className="flex flex-col p-4 gap-4 flex-1">
        {/* Back Button and Tabs */}
        <div className="flex gap-2">
          <button
            onClick={onBack}
            className="px-4 py-1 bg-blue-600 text-white font-bold rounded hover:bg-blue-700 flex items-center gap-2"
          >
            <span className="text-xl">←</span>
            <span>Quay lại</span>
          </button>
          <button
            onClick={() => setActiveTab('main')}
            className={`px-4 py-1 rounded font-bold ${
              activeTab === 'main'
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300'
            }`}
          >
            Chính
          </button>
          <button
            onClick={() => setActiveTab('dev')}
            className={`px-4 py-1 rounded font-bold ${
              activeTab === 'dev'
                ? 'bg-green-600 text-white'
                : 'bg-gray-700 text-gray-300'
            }`}
          >
            Dev
          </button>
        </div>

        {/* Tab Content */}
        <div className="flex-1 bg-gray-800 p-6 rounded flex items-center justify-center">
          {activeTab === 'main' && (
            <div className="flex flex-col items-center gap-4">
              <button
                onClick={onExit}
                className="px-6 py-3 bg-red-600 text-white text-lg font-bold rounded hover:bg-red-700"
              >
                Thoát game
              </button>
            </div>
          )}

          {activeTab === 'dev' && (
            <div className="flex flex-col items-center gap-1">
              <div className="flex gap-2">
                {/* Dice 1 */}
                <div className="flex flex-col items-center gap-2">
                  <div
                    onClick={() => setDevDice1(cycleDice(devDice1))}
                    className="w-8 h-8 bg-white border-4 border-gray-600 rounded-lg flex items-center justify-center cursor-pointer hover:bg-gray-100 transition-colors"
                  >
                    <span className="text-xl font-bold text-black">{devDice1}</span>
                  </div>
                </div>

                {/* Dice 2 */}
                <div className="flex flex-col items-center gap-2">
                  <div
                    onClick={() => setDevDice2(cycleDice(devDice2))}
                    className="w-8 h-8 bg-white border-4 border-gray-600 rounded-lg flex items-center justify-center cursor-pointer hover:bg-gray-100 transition-colors"
                  >
                    <span className="text-xl font-bold text-black">{devDice2}</span>
                  </div>
                </div>
              </div>

              <button
                onClick={handleDevRoll}
                disabled={!canRoll}
                className="px-4 py-2 bg-green-600 text-white font-bold rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >Thảy</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
