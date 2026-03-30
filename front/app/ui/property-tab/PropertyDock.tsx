import { GameBoardProps } from "../game-board/props";
import { formatBudget } from "@/app/utils/format";


export function PropertyDock(props: GameBoardProps) {
  const { gameData, selectedBds } = props;
  const bds = gameData.bds[selectedBds];
  if (!bds) return null;
  const group = bds.group;
  const groupColor = gameData.pallete[group];
  const fontSize = "5cqw";
  return (
    <div className="@container flex w-full h-full">
      <svg width="100%" height="100%">
        {/* Border */}
        <rect x="0" y="0" width="100%" height="100%" fill="white" stroke="black" strokeWidth="3" />

        {/* Color bar */}
        <rect x="95%" y="0" width="5%" height="100%" fill={groupColor} stroke="black" strokeWidth="2" />

        {/* Property ID */}
        <text x="2%" y="10%" fontSize="5cqw" textAnchor="start" fill="green">
          {selectedBds} - Giá {formatBudget(bds.price)}
          {bds.downgrade !== null && bds.downgrade !== undefined && `/HC: ${formatBudget(bds.downgrade)}`}
          /Ch: {formatBudget(bds.unmortgage)}
        </text>
        <text x="2%" y="23%" fontSize="6cqw" textAnchor="start" fill="chocolate">{bds.name}</text>

        {/* Rent levels - dynamically rendered based on rent array length */}
        {bds.rent.map((rentValue, index) => {
          const column = Math.floor(index / 5);
          const row = index % 5;
          const x = `${5 + 30 * column}%`;
          const y = `${35 + 7 * row}%`;

          return (
            <text
              key={index}
              x={x}
              y={y}
              fontSize={fontSize}
              textAnchor='start'
              fill="black"
            >
              Lv.{index + bds.level_start}: {formatBudget(rentValue)}
            </text>
          );
        })}

        {/* Separator line */}
        <line x1="5%" y1="68%" x2="90%" y2="68%" stroke="black" strokeWidth="1" />

        {/* Upgrade/Downgrade and Mortgage */}
        {(() => {
          let xPosition = 5;
          let yPosition = 78;
          const increment = 7;
          const elements = [];

          if (bds.upgrade !== null && bds.upgrade !== undefined) {
            elements.push(
              <text key="upgrade" x={`${xPosition}%`} y={`${yPosition}%`} fontSize={fontSize} fill="black">
                Nâng cấp: -{formatBudget(bds.upgrade)}
              </text>
            );
            yPosition += increment;
          }

          // Mortgage
          elements.push(
            <text
              key="mortgage"
              x={`${xPosition}%`} y={`${yPosition}%`}
              fontSize={fontSize}
              fill="black"
            >
              Cầm cố: +{formatBudget(bds.mortgage)}
            </text>
          );

          return elements;
        })()}
      </svg>
    </div>
  );
}

