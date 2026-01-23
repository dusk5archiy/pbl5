import { useState, useEffect } from 'react';
import TitleDeed from './TitleDeed';
import { GameData, GameState } from '@/app/game/model';
import { upgradeProperty, downgradeProperty, mortgageProperty, unmortgageProperty } from '@/app/game/data';

interface BDSTabProps {
  gameData: GameData;
  gameState: GameState;
  selectedPropertyId: string | null;
  onPropertySelect: (propertyId: string) => void;
  onGameStateUpdate: (newGameState: GameState) => void;
}

export default function BDSTab({
  gameData,
  gameState,
  selectedPropertyId,
  onPropertySelect,
  onGameStateUpdate
}: BDSTabProps) {
  // Get the property to display - default to first property of first group if null
  const getDefaultPropertyId = () => {
    const firstGroup = gameData.bds_groups_order[0];
    const firstProperty = gameData.group_bds[firstGroup]?.[0];
    return firstProperty || Object.keys(gameData.bds)[0];
  };

  const displayPropertyId = selectedPropertyId || getDefaultPropertyId();

  // Get the group of the displayed property
  const getPropertyGroup = (propertyId: string) => {
    return gameData.bds[propertyId]?.group || gameData.bds_groups_order[0];
  };

  const [selectedGroup, setSelectedGroup] = useState<string | null>(getPropertyGroup(displayPropertyId));

  // Initialize selection on mount if null
  useEffect(() => {
    if (!selectedPropertyId) {
      const defaultPropertyId = getDefaultPropertyId();
      onPropertySelect(defaultPropertyId);
    }
  }, []);

  // Get property state
  const propertyState = displayPropertyId ? gameState.bds[displayPropertyId] : null;
  const propertyInfo = displayPropertyId ? gameData.bds[displayPropertyId] : null;

  // Check if current player owns this property
  const currentPlayer = gameState.current_player;
  const isOwnedByCurrentPlayer = propertyState?.owner === currentPlayer;

  // Get action availability from backend (already calculated for current player only)
  const canUpgrade = propertyState?.can_upgrade || false;
  const canDowngrade = propertyState?.can_downgrade || false;
  const canMortgage = propertyState?.can_mortgage || false;
  const canUnmortgage = propertyState?.can_unmortgage || false;

  // Helper function to format price
  const formatPrice = (price: number) => {
    if (price >= 1000) {
      return `-${price / 1000}tr`;
    }
    return `-${price}k`;
  };

  // Action handlers
  const handleUpgrade = async () => {
    if (!canUpgrade || !displayPropertyId) return;
    try {
      const response = await upgradeProperty({
        game_state: gameState,
        property_id: displayPropertyId
      });
      onGameStateUpdate(response.new_game_state);
    } catch (error) {
      console.error('Error upgrading property:', error);
    }
  };

  const handleDowngrade = async () => {
    if (!canDowngrade || !displayPropertyId) return;
    try {
      const response = await downgradeProperty({
        game_state: gameState,
        property_id: displayPropertyId
      });
      onGameStateUpdate(response.new_game_state);
    } catch (error) {
      console.error('Error downgrading property:', error);
    }
  };

  const handleMortgage = async () => {
    if (!canMortgage || !displayPropertyId) return;
    try {
      const response = await mortgageProperty({
        game_state: gameState,
        property_id: displayPropertyId
      });
      onGameStateUpdate(response.new_game_state);
    } catch (error) {
      console.error('Error mortgaging property:', error);
    }
  };

  const handleUnmortgage = async () => {
    if (!canUnmortgage || !displayPropertyId) return;
    try {
      const response = await unmortgageProperty({
        game_state: gameState,
        property_id: displayPropertyId
      });
      onGameStateUpdate(response.new_game_state);
    } catch (error) {
      console.error('Error unmortgaging property:', error);
    }
  };

  return (
    <div className="w-auto h-full aspect-square flex flex-col gap-1 p-2 overflow-hidden">
      {/* Title Deed Card */}
      <div className='h-[50%] flex justify-center'>
        <div className="w-[75%] h-full">
          <TitleDeed
            gameData={gameData}
            gameState={gameState}
            propertyId={displayPropertyId}
          />
        </div>
      </div>
      {/* Property Selector */}
      <div className="flex-1 flex flex-col gap-1">
        {/* First row: Property groups */}
        <div className="flex flex-1 gap-1 px-1 py-1 overflow-x-auto bg-green-900">
          {gameData.bds_groups_order.map((group) => (
            <button
              key={group}
              onClick={() => {
                setSelectedGroup(group);
                const firstProperty = gameData.group_bds[group]?.[0];
                if (firstProperty) {
                  onPropertySelect(firstProperty);
                }
              }}
              className="text-[5vh] w-[30%] px-2 py-1 font-bold border-2 rounded shrink-0"
              style={{
                backgroundColor: selectedGroup === group ? "white" : "gray",
              }}
            >
              {group}
            </button>
          ))}
        </div>

        {/* Second row: Property IDs for selected group */}
        {selectedGroup && (
          <div className="text-[5vh] flex flex-1 gap-1 justify-center flex-wrap">
            {gameData.group_bds[selectedGroup]?.map((propertyId) => (
              <button
                key={propertyId}
                onClick={() => onPropertySelect(propertyId)}
                className="flex-1 px-2 font-bold border-2 rounded"
                style={{
                  backgroundColor: selectedPropertyId === propertyId ? "white" : "gray",
                  borderColor: 'black',
                }}
              >
                {propertyId}
              </button>
            ))}
          </div>
        )}

        {/* Action buttons */}
      </div>
      <div className="grid grid-cols-2 gap-1">
        <button
          onClick={handleUpgrade}
          disabled={!canUpgrade}
          className="text-[5vh] px-1 py-1 bg-[lightgreen] rounded"
          style={{ color: canUpgrade ? 'black' : 'white' }}
        >
          Nâng cấp{isOwnedByCurrentPlayer && propertyInfo?.upgrade ? ` (${formatPrice(propertyInfo.upgrade)})` : ''}
        </button>
        <button
          onClick={handleDowngrade}
          disabled={!canDowngrade}
          className="text-[5vh] px-1 py-1 bg-[salmon] rounded"
          style={{ color: canDowngrade ? 'black' : 'white' }}
        >
          Hạ cấp{isOwnedByCurrentPlayer && propertyInfo?.downgrade ? ` (+${propertyInfo.downgrade}k)` : ''}
        </button>
        <button
          onClick={handleMortgage}
          disabled={!canMortgage}
          className="text-[5vh] px-1 py-1 bg-[lightgray] rounded"
          style={{ color: canMortgage ? 'black' : 'white' }}
        >
          Cầm cố{isOwnedByCurrentPlayer && propertyInfo?.mortgage ? ` (+${propertyInfo.mortgage}k)` : ''}
        </button>
        <button
          onClick={handleUnmortgage}
          disabled={!canUnmortgage}
          className="text-[5vh] px-1 py-1 bg-[lightgray] rounded"
          style={{ color: canUnmortgage ? 'black' : 'white' }}
        >
          Chuộc{isOwnedByCurrentPlayer && propertyInfo?.unmortgage ? ` (${formatPrice(propertyInfo.unmortgage)})` : ''}
        </button>
      </div>
    </div>
  );
}
