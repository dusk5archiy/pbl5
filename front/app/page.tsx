export default function Home() {
  return (
    <div className="flex flex-col gap-4 h-screen bg-gray-900">
      <div className="bg-teal-900 p-4 font-bold">PBL5 - Dự án kĩ thuật máy tính</div>
      <div className="flex flex-col m-4 grow gap-4 items-center">
        <div className="h-[5vh]"></div>
        <div className="text-center text-2xl font-bold uppercase font-[bahnschrift]">Hệ thống nhận diện xúc xắc và hỗ trợ người chơi cờ tỷ phú</div>
        <div className="flex grow h-full w-full justify-center items-center">
          <button className="bg-red-800 active:bg-red-900 w-fit h-fit px-8 py-4 rounded-lg text-xl uppercase font-[bahnschrift] font-bold">Bắt đầu</button>
        </div>
        <div className="h-[25vh]"></div>
      </div>
    </div>
  );
}
