import { ActionCardPanel } from "./ActionCardPanel";
import { ActionCardModal } from "./ActionCardModal";
import { ActionCardSelector } from "./ActionCardSelector";
import { PropertyPanelProps } from "./props";

export function ActionCardTab(props: PropertyPanelProps) {
  return (
    <div className="w-full h-full flex gap-[2%]">
      <div className="w-[50vw] h-full gap-[1vw] flex flex-col justify-center">
        <div className="@container w-full h-[70%] flex rounded bg-emerald-200">
          <ActionCardModal {...props} />
        </div>
        <div className="w-full h-[30%] flex">
          <ActionCardPanel {...props} />
        </div>
      </div>
      <div className="h-full flex flex-1">
        <ActionCardSelector {...props} />
      </div>
    </div>
  );
}

