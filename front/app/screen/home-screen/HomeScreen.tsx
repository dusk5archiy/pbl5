export default function HomeScreen(
  props: {
    onStart: () => void,
    onJoin: () => void,
  }
) {
  const { onStart, onJoin } = props;
  return (
    <div className="w-screen h-screen flex flex-col">
      <div className="w-full text-center font-bold text-[5vh] mt-[5vh] mb-[5vh]">Monopoly Impact 5</div>
      <div className="w-full h-full flex flex-col gap-2 items-center">
        <div className="flex gap-2">
          <button
            onClick={onStart}
            className="w-max px-[2vw] py-[2vh] text-[4vh] bg-green-300 active:bg-green-500 rounded">Tạo phòng
          </button>
          <button
            onClick={onJoin}
            className="w-max px-[2vw] py-[2vh] text-[4vh] bg-red-300 active:bg-red-500 rounded">Vào phòng
          </button>
        </div>
      </div>
    </div>
  );
}
