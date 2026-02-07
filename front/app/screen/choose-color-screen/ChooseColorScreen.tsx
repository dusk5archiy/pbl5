'use client'

import { ChooseColorScreenProps } from "./props";
import { ColorInputViewer } from "./ColorInputViewer";
import { ColorOutputViewer } from "./ColorOutputViewer";
import { CSSProperties } from "react";

export default function ChooseColorScreen(props: ChooseColorScreenProps) {
  const { onBack, onNext, version, setVersion, diceDetection, setDiceDetection, getSelectedColors } = props;
  const versions = ["1", "2", "5"];

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
          <div className="w-full flex">
            <div className="w-[50%] flex flex-col items-center gap-[0.5vw]">
              <div className="text-[2vw]">Chọn phiên bản trò chơi</div>
              <div className="w-full flex gap-[2vw] justify-evenly">
                {
                  versions.map(
                    (v) =>
                      <button
                        key={v}
                        style={
                          {
                            "--bg-color": version == v ? "#b9f8cf" : "white"
                          } as CSSProperties
                        }
                        className="px-[2vw] py-[1vw] bg-(--bg-color) border border-gray-400 rounded-xl text-[2vw]"
                        onClick={() => setVersion(v)}
                      >
                        {v}
                      </button>
                  )
                }
              </div>
            </div>
            <div className="w-[50%] flex flex-col items-center gap-[0.5vw]">
              <div className="text-[2vw]">Nhận diện xúc xắc qua camera?</div>
              <div className="w-full flex gap-[1.5vw] justify-evenly">
                <button
                  style={
                    {
                      "--bg-color": !diceDetection ? "#fca5a5" : "white"
                    } as CSSProperties
                  }
                  className="px-[2vw] py-[1vw] bg-(--bg-color) border border-gray-400 rounded-xl text-[2vw] "
                  onClick={() => setDiceDetection(false)}
                >
                  Không
                </button>
                <button
                  style={
                    {
                      "--bg-color": diceDetection ? "#b9f8cf" : "white"
                    } as CSSProperties
                  }
                  className="px-[2vw] py-[1vw] bg-(--bg-color) border border-gray-400 rounded-xl text-[2vw] "
                  onClick={() => setDiceDetection(true)}
                >
                  Có
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="w-full flex py-[2vh] justify-center">
        <button
          className="w-max h-max px-[2vw] py-[2vh] text-[2vw] font-bold text-gray-600 hover:text-gray-800 rounded bg-green-200 disabled:text-white active:bg-green-400 disabled:active:bg-green-200"
          onClick={onNext}
          disabled={getSelectedColors.length < 2}
        >
          Tiếp tục
        </button>
      </div>
    </div>
  );
}
