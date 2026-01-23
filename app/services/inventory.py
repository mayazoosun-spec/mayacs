"""库存服务"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import Inventory, InventoryTransaction, TransactionType
from app.schemas.inventory import InventoryCreate, InventoryUpdate, InventoryTransactionCreate


class InventoryService:
    """库存服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_inventory(self, data: InventoryCreate) -> Inventory:
        """创建库存记录"""
        inventory = Inventory(**data.model_dump())
        inventory.available_quantity = inventory.quantity - inventory.reserved_quantity
        self.db.add(inventory)
        await self.db.flush()
        await self.db.refresh(inventory)
        return inventory

    async def get_inventory(self, inventory_id: int) -> Optional[Inventory]:
        """获取库存记录"""
        result = await self.db.execute(
            select(Inventory).where(Inventory.id == inventory_id)
        )
        return result.scalar_one_or_none()

    async def get_inventory_by_product_store(
        self, product_id: int, store_id: int
    ) -> Optional[Inventory]:
        """通过产品和门店获取库存"""
        result = await self.db.execute(
            select(Inventory).where(
                Inventory.product_id == product_id,
                Inventory.store_id == store_id
            )
        )
        return result.scalar_one_or_none()

    async def get_inventories(
        self,
        product_id: Optional[int] = None,
        store_id: Optional[int] = None,
        low_stock: bool = False,
    ) -> List[Inventory]:
        """获取库存列表"""
        query = select(Inventory)

        if product_id:
            query = query.where(Inventory.product_id == product_id)
        if store_id:
            query = query.where(Inventory.store_id == store_id)
        if low_stock:
            query = query.where(Inventory.quantity <= Inventory.min_quantity)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_inventory(
        self, inventory_id: int, data: InventoryUpdate
    ) -> Optional[Inventory]:
        """更新库存"""
        inventory = await self.get_inventory(inventory_id)
        if not inventory:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(inventory, key, value)

        # 重新计算可用库存
        inventory.available_quantity = inventory.quantity - inventory.reserved_quantity

        await self.db.flush()
        await self.db.refresh(inventory)
        return inventory

    async def adjust_inventory(
        self, data: InventoryTransactionCreate
    ) -> InventoryTransaction:
        """库存调整(入库/出库)"""
        inventory = await self.get_inventory(data.inventory_id)
        if not inventory:
            raise ValueError("库存记录不存在")

        # 记录变动前数量
        quantity_before = inventory.quantity

        # 更新库存数量
        inventory.quantity += data.quantity_change
        if inventory.quantity < 0:
            raise ValueError("库存不足")

        # 更新可用库存
        inventory.available_quantity = inventory.quantity - inventory.reserved_quantity

        # 创建变动记录
        transaction = InventoryTransaction(
            inventory_id=data.inventory_id,
            transaction_type=data.transaction_type,
            quantity_change=data.quantity_change,
            quantity_before=quantity_before,
            quantity_after=inventory.quantity,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            remark=data.remark,
            operator=data.operator,
        )
        self.db.add(transaction)

        await self.db.flush()
        await self.db.refresh(transaction)
        return transaction

    async def reserve_inventory(
        self, inventory_id: int, quantity: int
    ) -> bool:
        """预留库存"""
        inventory = await self.get_inventory(inventory_id)
        if not inventory:
            return False

        if inventory.available_quantity < quantity:
            return False

        inventory.reserved_quantity += quantity
        inventory.available_quantity = inventory.quantity - inventory.reserved_quantity

        await self.db.flush()
        return True

    async def release_inventory(
        self, inventory_id: int, quantity: int
    ) -> bool:
        """释放预留库存"""
        inventory = await self.get_inventory(inventory_id)
        if not inventory:
            return False

        inventory.reserved_quantity = max(0, inventory.reserved_quantity - quantity)
        inventory.available_quantity = inventory.quantity - inventory.reserved_quantity

        await self.db.flush()
        return True

    async def get_transactions(
        self,
        inventory_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> List[InventoryTransaction]:
        """获取库存变动记录"""
        result = await self.db.execute(
            select(InventoryTransaction)
            .where(InventoryTransaction.inventory_id == inventory_id)
            .order_by(InventoryTransaction.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
