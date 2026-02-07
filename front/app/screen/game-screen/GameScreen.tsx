'use client'

import { GameScreenProps } from "./props";
import { GamePresentation } from "./GamePresentation";

export function GameScreen(props: GameScreenProps) {
  return (<GamePresentation {...props} />);
}
