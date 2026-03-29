import { COLOR_UI_INFO, ColorUIInfo } from "@/app/utils/pallete";

export function getColorButtonHandler(
  props: {
    getSelectedColors: string[],
    setSelectedColors: (_: string[]) => void
  }
) {
  const { getSelectedColors, setSelectedColors } = props;
  return (color: string) => {
    if (!getSelectedColors.find(c => c === color)) {
      setSelectedColors([...getSelectedColors, color]);
    }
  };

}

function getColorButtonMapping(
  props: {
    getSelectedColors: string[],
    setSelectedColors: (_: string[]) => void
  }
) {
  const { getSelectedColors } = props;
  const handleColorButton = getColorButtonHandler(props);
  return ([id, ui_info]: [string, ColorUIInfo]) => {
    const is_disabled = getSelectedColors.find(c => c === id) !== undefined;
    return (
      <button
        key={id}
        onClick={() => handleColorButton(id)}
        disabled={is_disabled}
        style={
          {
            '--bg-color': ui_info.lightColorCode,
          } as React.CSSProperties
        }
        className="h-full aspect-square text-[2vw] bg-(--bg-color) rounded hover:underline active:font-bold active:no-underline disabled:bg-gray-400"
      >{is_disabled ? '' : ui_info.uiName}</button>
    );
  };
}

export function ColorInputViewer(
  props: {
    getSelectedColors: string[],
    setSelectedColors: (_: string[]) => void
  }
) {
  const colorButtonMapping = getColorButtonMapping(props);
  return (
    <div className="w-full flex flex-col gap-[2vh] items-center">
      <div className="text-[2vw]">Chọn trong số những màu dưới đây theo thứ tự mong muốn:</div>
      <div className="w-full h-[15vh] flex gap-[2vw] justify-between items-center overflow-auto">
        {
          Object.entries(COLOR_UI_INFO).map(colorButtonMapping)
        }
      </div>
    </div>
  );
};
