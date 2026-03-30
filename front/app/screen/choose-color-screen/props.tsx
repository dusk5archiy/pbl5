export interface ChooseColorScreenProps {
  onBack: () => void;
  onNext: () => void;
  getSelectedColors: string[],
  setSelectedColors: (_: string[]) => void;
  version: string;
  setVersion: (_: string) => void;
  diceDetection: boolean;
  setDiceDetection: (_: boolean) => void;
}
