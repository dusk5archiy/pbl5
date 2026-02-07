import { COLOR_UI_INFO } from "@/app/utils/pallete";
import { PropertyPanelProps } from "./props";
import { CSSProperties } from "react";

export function PropertyStatePanel(props: PropertyPanelProps) {
  const { gameState, selectedBds } = props;
  const house = gameState.logic.build.house;
  const hotel = gameState.logic.build.hotel;
  const skyscraper = gameState.logic.build.skyscraper;
  const level = gameState.ui.bds[selectedBds].level;
  const owner = gameState.logic.bds[selectedBds].owner;
  const level_content = level >= 0 ? level : "-";
  const elements = [
    {
      label: "Nhà",
      amount: house
    },
    {
      label: "K.sạn",
      amount: hotel
    },
    {
      label: "NC.tầng",
      amount: skyscraper
    },
  ];

  const text_color = owner == null ? "text-gray-100" : "text-black";


  return (
    <div className="w-full h-full flex gap-[0.5vw] justify-between">
      {
        elements.map(({ label, amount }) =>
          <div key={label} className="flex-1 h-full flex flex-col justify-center px-[0.5vw] border-2 border-white rounded">
            <div className="w-full flex justify-center text-gray-100 text-[2cqw]">
              {label}
            </div>
            <div className="w-full flex justify-center text-gray-100 font-bold text-[3cqw]">
              {amount}
            </div>
          </div>
        )
      }
      <div key={"level"}
        style={
          {
            "--bg-color": owner == null ? undefined : COLOR_UI_INFO[owner].lightColorCode
          } as CSSProperties
        }
        className={
          `flex-1 h-full flex flex-col justify-center px-[0.5vw] border-2 border-white rounded ${owner == null ? "" : `bg-(--bg-color)`}`
        }>
        <div className={`w-full flex justify-center ${text_color} text-[2cqw]`}>Cấp</div>
        <div className={`w-full flex justify-center ${text_color} font-bold text-[3cqw]`}>
          {level_content}
        </div>
      </div>
    </div>
  );

}
