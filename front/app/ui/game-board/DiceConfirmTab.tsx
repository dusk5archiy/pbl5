import { GameBoardProps } from "./props";
import { useRef, useEffect } from "react";

export function DiceConfirmTab(props: GameBoardProps) {
  const { diceDetectionResult, setDiceDetectionResult, encodedImage, setEncodedImage, sendRollDice } = props;
  const canvasRef = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    if (canvasRef.current && encodedImage != null && diceDetectionResult != null) {
      const padding = 50;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');
      if (ctx) {
        const img = new Image();
        img.onload = () => {
          canvas.width = img.width + 2 * padding;
          canvas.height = img.height + 2 * padding;
          ctx.drawImage(img, padding, padding);

          // Draw bounding boxes and scores
          ctx.lineWidth = 5;
          ctx.font = '5vw sans-serif';
          diceDetectionResult.bboxes.forEach((bbox, index) => {
            const [x, y, w, h] = bbox;
            ctx.strokeStyle = 'blue';
            ctx.strokeRect(x + padding, y + padding, w, h);
            ctx.fillStyle = 'red';
            ctx.fillText(diceDetectionResult.scores[index].toString(), x + padding, y + padding - 10);
          });
        };
        img.src = encodedImage;
      }
    }
  }, [encodedImage, diceDetectionResult]);
  const buttonClassName = "px-[4cqw] py-[2cqw] rounded disabled:text-white disabled:bg-gray-300 border-2 border-white";
  const disabled = diceDetectionResult?.scores.length != 2;

  return (
    <div className="w-full h-full flex flex-col gap-[1.5vw]">
      <div className="w-full h-[70%] flex">
        <canvas ref={canvasRef} className="w-full h-full object-contain" />
      </div>
      <div className="w-full flex justify-evenly px-[1.5vw] gap-[1.5vw] text-[3cqw]">
        <button
          className={buttonClassName + " bg-green-300"}
          disabled={disabled}
          onClick={
            () => {
              if (diceDetectionResult?.scores.length != 2) {
                return;
              }
              const dice_1 = `${diceDetectionResult.scores[0]}`;
              const dice_2 = `${diceDetectionResult.scores[1]}`;
              sendRollDice({ dice_1: dice_1, dice_2: dice_2 });
            }
          }
        >Xác nhận</button>
        <button
          className={buttonClassName + " bg-yellow-300"}
          onClick={() => {
            setEncodedImage(null);
            setDiceDetectionResult(null);
          }}
        >Chụp lại
        </button>
      </div>
    </div>
  );
}
