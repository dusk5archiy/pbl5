'use client';

interface WelcomeScreenProps {
  onStart: () => void;
}

export default function WelcomeScreen({ onStart }: WelcomeScreenProps) {
  return (
    <div className="flex flex-col gap-4 h-screen bg-gray-100">
      <div className="bg-green-200 p-4 font-bold">PBL5 - Dự án kĩ thuật máy tính</div>
      <div className="flex flex-col m-4 grow gap-4 items-center">
        <div className="h-[5vh]"></div>
        <div className="text-center font-bold uppercase font-[bahnschrift] text-sm">Hệ thống nhận diện xúc xắc và hỗ trợ người chơi cờ tỷ phú</div>
        <div className="flex grow h-full w-full justify-center items-center">
          <button
            onClick={onStart}
            className="bg-red-300 active:bg-red-400 w-fit h-fit px-4 py-2 rounded-lg text-lg uppercase font-[bahnschrift] font-bold"
          >
            Bắt đầu
          </button>
        </div>
        <div className="h-[25vh]"></div>
      </div>
    </div>
  );
}
