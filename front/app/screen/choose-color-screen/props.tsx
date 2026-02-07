import { Dispatch, SetStateAction } from "react";

export interface ChooseColorScreenProps {
  onBack: () => void;
  onNext: () => void;
  getSelectedColors: string[],
  setSelectedColors: Dispatch<SetStateAction<string[]>>
  version: string;
  setVersion: (_: string) => void;
  diceDetection: boolean;
  setDiceDetection: (_: boolean) => void;
}
