'use client'

interface HomeScreenProps {
  onStart: () => void
}

export default function HomeScreen({ onStart }: HomeScreenProps) {
  return (
    <div className="w-screen h-screen flex flex-col">
      <div className="w-full text-center font-bold text-[5vh] mt-[5vh] mb-[5vh]">Monopoly Impact 5</div>
      <div className="w-full h-full flex flex-col items-center">
        <button
          onClick={onStart}
          className="w-max px-[2vw] py-[2vh] text-[4vh] bg-green-300 hover:bg-green-400 active:bg-green-500 rounded">Bắt đầu</button>
      </div>
    </div>
  );
}
