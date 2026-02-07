import { PropertyStatePanel } from "./BuildPanel";
import { MortgagePanel as PropertyUpgradePanel } from "./PropertyUpgradePanel";
import { PropertyDock } from "./PropertyDock";
import { PropertySelector } from "./PropertySelector";
import { PropertyPanelProps } from "./props";

export function PropertyTab(props: PropertyPanelProps) {
  return (
    <div className="w-full h-full flex flex-col gap-[1vw]">
      <div className="w-full h-[65%] flex gap-[1vw]">
        <div className="w-[40%] h-full flex justify-center">
          {PropertyDock(props)}
        </div>
        <div className="h-full flex flex-1">
          {PropertySelector(props)}
        </div>
      </div>
      <div className="w-full h-[35%] flex items-center gap-[1vw] overflow-hidden">
        <div className="w-[40%] h-[70%] flex">
          {PropertyStatePanel(props)}
        </div>
        <div className="flex-1 h-full flex overflow-hidden">
          {PropertyUpgradePanel(props)}
        </div>
      </div>
    </div>
  );
}
