import { useState, useEffect } from 'react';
import TitleDeed from './TitleDeed';
import { GameData, GameState } from '@/app/game/model';

interface BDSTabProps {
  gameData: GameData;
  gameState: GameState;
  selectedPropertyId: string | null;
  onPropertySelect: (propertyId: string) => void;
}

export default function BDSTab({
  gameData,
  gameState,
  selectedPropertyId,
  onPropertySelect
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

  return (
    <div className="h-full aspect-square flex flex-col gap-2 p-2">
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
      <div className="flex-1 flex flex-col gap-2">
        {/* First row: Property groups */}
        <div className="flex gap-1 justify-center">
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
              className="text-[3vh] px-2 py-1 font-bold border-2 rounded"
              style={{
                backgroundColor: gameData.color_pallete.groups[group],
                borderColor: selectedGroup === group ? 'white' : 'black',
                opacity: selectedGroup === group ? 1 : 0.7
              }}
            >
              {group}
            </button>
          ))}
        </div>

        {/* Second row: Property IDs for selected group */}
        {selectedGroup && (
          <div className="text-[3vh] flex gap-1 justify-center flex-wrap">
            {gameData.group_bds[selectedGroup]?.map((propertyId) => (
              <button
                key={propertyId}
                onClick={() => onPropertySelect(propertyId)}
                className="px-2 py-1 font-bold border-2 rounded"
                style={{
                  backgroundColor: selectedPropertyId === propertyId ? gameData.color_pallete.groups[selectedGroup] : 'white',
                  borderColor: 'black',
                }}
              >
                {propertyId}
              </button>
            ))}
          </div>
        )}

        {/* Action buttons */}
        <div className="grid grid-cols-2 gap-2 mt-auto">
          <button className="text-[5vh] px-4 py-1 bg-[lightgreen] text-white rounded">
            Nâng cấp
          </button>
          <button className="text-[5vh] px-4 py-1 bg-[salmon] text-white rounded">
            Hạ cấp
          </button>
          <button className="text-[5vh] px-4 py-1 bg-[lightgray] text-white rounded">
            Cầm cố
          </button>
          <button className="text-[5vh] px-4 py-1 bg-[lightgray] text-white rounded">
            Chuộc
          </button>
        </div>
      </div>
    </div>
  );
}
