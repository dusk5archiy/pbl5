'use client'

import { ChooseColorScreenProps } from "./props";
import { COLOR_UI_INFO } from "@/app/utils/pallete";

function ColorComponent(id: string) {
  return (
    <div
      key={id}
      style={
        {
          '--bg-color': COLOR_UI_INFO[id].lightColorCode,
        } as React.CSSProperties
      }
      className="h-[70%] w-max px-[2vh] text-[3vh] bg-(--bg-color) flex items-center justify-center rounded"
    >{COLOR_UI_INFO[id].uiName}</div>
  );
}

export function ColorOutputViewer(props: ChooseColorScreenProps) {
  const { getSelectedColors, setSelectedColors } = props;
  return (
    <div className="w-full flex flex-col gap-[2vh] items-center">
      <div className="text-[2vw]">Thứ tự màu đã chọn:</div>
      <div className="w-full flex gap-[2vw] justify-between items-center">
        <button
          onClick={() => setSelectedColors([])}
          className="w-max h-max px-[2vw] py-[2vh] text-[2vw] font-bold text-gray-600 hover:text-gray-800 rounded bg-gray-200 hover:bg-gray-300 active:bg-gray-400"
        >Làm mới</button>
        <div className="flex-1 h-[10vh] flex px-[2vw] gap-[2vw] items-center rounded bg-gray-200 overflow-auto">
          {getSelectedColors.map(ColorComponent)}
        </div>
      </div>
    </div>
  );
};

