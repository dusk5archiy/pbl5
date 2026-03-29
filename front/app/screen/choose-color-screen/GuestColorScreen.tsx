import { ColorInputViewer } from "./ColorInputViewer";
import { ColorOutputViewer } from "./ColorOutputViewer";

export default function GuestColorScreen(
  props: {
    onBack: () => void;
    onNext: () => void;
    getSelectedColors: string[],
    setSelectedColors: (_: string[]) => void,
  }
) {
  const { onBack, onNext, getSelectedColors } = props;

  return (
    <div className="w-screen h-screen px-[2vw] py-[2vh] gap-[2vh] flex flex-col">
      <div className="w-full flex gap-[2vw] mb-[2vh]">
        <button
          onClick={onBack}
          className="w-max h-max px-[2vw] py-[2vh] text-[3vh] font-bold text-gray-600 hover:text-gray-800 rounded bg-blue-200 hover:bg-blue-300 active:bg-blue-400"
        >Trở về</button>
        <div className="h-full flex font-bold text-[4vh] items-center">Chọn màu</div>
      </div>
      <div className="w-full flex flex-col items-center">
        <div className="w-[70%] flex flex-col gap-[3vh] items-center">
          <ColorInputViewer {...props} />
          <ColorOutputViewer {...props} />
        </div>
      </div>
      <div className="w-full flex py-[2vh] justify-center">
        <button
          className="w-max h-max px-[2vw] py-[2vh] text-[2vw] font-bold text-gray-600 hover:text-gray-800 rounded bg-green-200 disabled:text-white active:bg-green-400 disabled:active:bg-green-200"
          onClick={onNext}
          disabled={getSelectedColors.length != 1}
        >
          Tiếp tục
        </button>
      </div>
    </div>
  );
}
