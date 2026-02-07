from pydantic import BaseModel
import math


class BDSModel(BaseModel):
    name: str
    price_group: str


class PriceGroupModel(BaseModel):
    group: str
    type: int = 0
    price: int
    level_start: int = 0
    rent: list[int]
    upgrade: int | None = None


class BDS(BaseModel):
    name: str
    group: str
    price: int
    rent: list[int]
    level_start: int
    upgrade: int | None = None
    downgrade: int | None = None
    mortgage: int
    unmortgage: int


class BDSGroup(BaseModel):
    bds: list[str]
    type: int


class BDSDataModel(BaseModel):
    bds: dict[str, BDSModel]
    price_groups: dict[str, PriceGroupModel]

    def export(self):
        bds = {}
        bds_group: dict[str, BDSGroup] = {}
        for bds_id in self.bds.keys():
            bds_model = self.bds[bds_id]
            price_group = self.price_groups[bds_model.price_group]
            upgrade = price_group.upgrade
            downgrade = None if upgrade is None else math.ceil(upgrade / 2)
            mortgage = price_group.price // 2
            unmortgage = mortgage + mortgage // 10
            group = price_group.group

            bds[bds_id] = BDS(
                name=bds_model.name,
                level_start=price_group.level_start,
                group=group,
                price=price_group.price,
                rent=price_group.rent,
                upgrade=price_group.upgrade,
                downgrade=downgrade,
                mortgage=mortgage,
                unmortgage=unmortgage,
            )

            if group not in bds_group:
                bds_group[group] = BDSGroup(bds=[bds_id], type=price_group.type)
            else:
                bds_group[group].bds.append(bds_id)

        return bds, bds_group
