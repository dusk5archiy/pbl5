import React from 'react';
import { GameData, GameState } from '@/app/game/model';
import { formatBudget } from './lib/utils';

interface TitleDeedProps {
  gameData: GameData;
  gameState: GameState;
  propertyId: string
}

const TitleDeed: React.FC<TitleDeedProps> = ({
  gameData,
  gameState,
  propertyId,
}) => {
  const property = gameData.bds[propertyId];
  if (!property) return null;

  const groupColor = gameData.color_pallete.groups[property.group];
  const fontSize = "75%";
  const propertyState = gameState.bds[propertyId];
  const currentLevel = propertyState?.level ?? -1;
  const isOwned = propertyState?.owner && propertyState.owner !== "";

  return (
    <svg width="100%" height="100%">
      {/* Border */}
      <rect x="0" y="0" width="100%" height="100%" fill="white" stroke="black" strokeWidth="3" />

      {/* Color bar at top */}
      <rect x="95%" y="0" width="5%" height="100%" fill={groupColor} stroke="black" strokeWidth="2" />

      {/* Property ID */}
      <text x="2%" y="10%" fontSize="55%" textAnchor="start" fill="green">
        {propertyId} - Giá {formatBudget(property.price)}
        {property.downgrade !== null && property.downgrade !== undefined && `/HC: ${formatBudget(property.downgrade)}`}
        /Ch: {formatBudget(property.unmortgage)}
      </text>
      <text x="2%" y="21%" fontSize="80%" textAnchor="start" fill="chocolate">
        {property.name}
      </text>

      {/* Rent levels - dynamically rendered based on rent array length */}
      {property.rent.map((rentValue, index) => {
        const column = index < Math.ceil(property.rent.length / 2) ? 0 : 1;
        const row = index < Math.ceil(property.rent.length / 2) ? index : index - Math.ceil(property.rent.length / 2);
        const x = column === 0 ? "10%" : "50%";
        const y = `${35 + row * 10}%`;
        const isBold = isOwned && index === currentLevel;

        return (
          <text 
            key={index} 
            x={x} 
            y={y} 
            fontSize={fontSize} 
            textAnchor='start' 
            fill="black"
            fontWeight={isBold ? "bold" : "normal"}
          >
            {isBold && '• '}Lv.{index}: {formatBudget(rentValue)}
          </text>
        );
      })}

      {/* Separator line */}
      <line x1="10%" y1="60%" x2="80%" y2="60%" stroke="black" strokeWidth="1" />

      {/* Upgrade/Downgrade and Mortgage - dynamically positioned */}
      {(() => {
        let yPosition = 71;
        const lineIncrement = 10;
        const elements = [];
        const isMortgaged = isOwned && currentLevel === -1;

        if (property.upgrade !== null && property.upgrade !== undefined) {
          elements.push(
            <text key="upgrade" x="10%" y={`${yPosition}%`} fontSize={fontSize} fill="black">
              Nâng cấp: -{formatBudget(property.upgrade)}
            </text>
          );
          yPosition += lineIncrement;
        }

        // Add mortgage
        elements.push(
          <text 
            key="mortgage" 
            x="10%" 
            y={`${yPosition}%`} 
            fontSize={fontSize} 
            fill="black"
            fontWeight={isMortgaged ? "bold" : "normal"}
          >
            {isMortgaged && '• '}Cầm cố: +{formatBudget(property.mortgage)}
          </text>
        );

        return elements;
      })()}
    </svg>
  );
}

export default TitleDeed;
