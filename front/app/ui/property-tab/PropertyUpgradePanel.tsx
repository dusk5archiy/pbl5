import { formatBudget } from "@/app/utils/format";
import { CSSProperties } from "react";
import { GameBoardProps } from "./props";

export function MortgagePanel(props: GameBoardProps) {
  const { upgradeBdsFunc, downgradeBdsFunc, mortgageBdsFunc, unmortgageBdsFunc, setPropertyTab, guest } = props;
  const buttonClassName = "flex-1 h-full flex flex-col justify-center overflow-hidden rounded border-2 border-white disabled:text-white whitespace-nowrap bg-(--bg-color) active:bg-gray-400 disabled:active:bg-(--bg-color)";
  const { selectedBds, gameState, tradeFunc } = props;
  const upgrade_amount = gameState.ui.bds[selectedBds].upgrade_amount;
  const downgrade_amount = gameState.ui.bds[selectedBds].downgrade_amount;
  const mortgage_amount = gameState.ui.bds[selectedBds].mortgage_amount;
  const unmortgage_amount = gameState.ui.bds[selectedBds].unmortgage_amount;
  const can_interact = guest == null || guest == gameState.logic.viewing_player;

  const trade_chore = gameState.current_chore.trade;
  const can_choose = can_interact && gameState.ui.bds[selectedBds].can_choose;

  return (
    <div className="@container w-full h-full grid grid-cols-4 grid-rows-2 gap-[0.5vw]">
      <button
        style={{ "--bg-color": "#6EE7B7" } as CSSProperties}
        className={buttonClassName}
        disabled={!can_interact || !gameState.ui.bds[selectedBds].can_upgrade}
        onClick={() => upgradeBdsFunc({ bds: selectedBds })}
      >
        <div className="text-[3cqw]">Nâng cấp</div>
        {upgrade_amount != null && <div className="text-[5cqh]">{`-${formatBudget(upgrade_amount)}`}</div>}
      </button>
      <button
        style={{ "--bg-color": "#FCA5A5" } as CSSProperties}
        className={buttonClassName}
        disabled={!can_interact || !gameState.ui.bds[selectedBds].can_downgrade}
        onClick={() => downgradeBdsFunc({ bds: selectedBds })}
      >
        <div className="text-[3cqw]">Hạ cấp</div>
        {downgrade_amount != null && <div className="text-[5cqh]">{`+${formatBudget(downgrade_amount)}`}</div>}
      </button>
      <button
        style={{ "--bg-color": "#D1D5DB" } as CSSProperties}
        className={buttonClassName}
        disabled={!can_interact || !gameState.ui.bds[selectedBds].can_mortgage}
        onClick={() => mortgageBdsFunc({ bds: selectedBds })}
      >
        <div className="text-[3cqw]">Cầm cố</div>
        {mortgage_amount != null && <div className="text-[5cqh]">{`+${formatBudget(mortgage_amount)}`}</div>}
      </button>
      <button
        style={{ "--bg-color": "#D1D5DB" } as CSSProperties}
        className={buttonClassName}
        disabled={!can_interact || !gameState.ui.bds[selectedBds].can_unmortgage}
        onClick={() => unmortgageBdsFunc({ bds: selectedBds })}
      >
        <div className="text-[3cqw]">Chuộc</div>
        {unmortgage_amount != null && <div className="text-[5cqh]">{`-${formatBudget(unmortgage_amount)}`}</div>}
      </button>
      <button
        style={{ "--bg-color": "#D1D5DB" } as CSSProperties}
        className={buttonClassName}
        disabled={!can_choose}
        onClick={trade_chore != null ? () => {
          tradeFunc({ bds: selectedBds });
          setPropertyTab("trade");
        } : undefined}
      >
        <div className="text-[3cqw] font-bold">Chọn</div>
      </button>
    </div>
  );
}
