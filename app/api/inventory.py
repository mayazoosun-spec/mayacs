"""库存管理API"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.inventory import InventoryService
from app.schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse,
    InventoryTransactionCreate,
    InventoryTransactionResponse,
)

router = APIRouter()


@router.post("", response_model=InventoryResponse, summary="创建库存记录")
async def create_inventory(
    data: InventoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建产品在某门店/仓库的库存记录"""
    service = InventoryService(db)

    # 检查是否已存在
    existing = await service.get_inventory_by_product_store(
        data.product_id, data.store_id
    )
    if existing:
        raise HTTPException(
            status_code=400,
            detail="该产品在此门店的库存记录已存在"
        )

    return await service.create_inventory(data)


@router.get("", response_model=List[InventoryResponse], summary="获取库存列表")
async def get_inventories(
    product_id: Optional[int] = None,
    store_id: Optional[int] = None,
    low_stock: bool = Query(False, description="只显示低库存"),
    db: AsyncSession = Depends(get_db)
):
    """获取库存列表，支持按产品、门店筛选"""
    service = InventoryService(db)
    return await service.get_inventories(
        product_id=product_id,
        store_id=store_id,
        low_stock=low_stock,
    )


@router.get("/{inventory_id}", response_model=InventoryResponse, summary="获取库存详情")
async def get_inventory(
    inventory_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个库存记录详情"""
    service = InventoryService(db)
    inventory = await service.get_inventory(inventory_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="库存记录不存在")
    return inventory


@router.put("/{inventory_id}", response_model=InventoryResponse, summary="更新库存")
async def update_inventory(
    inventory_id: int,
    data: InventoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新库存信息(如预警值)"""
    service = InventoryService(db)
    inventory = await service.update_inventory(inventory_id, data)
    if not inventory:
        raise HTTPException(status_code=404, detail="库存记录不存在")
    return inventory


@router.post("/adjust", response_model=InventoryTransactionResponse, summary="库存调整")
async def adjust_inventory(
    data: InventoryTransactionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    库存调整(入库/出库)
    - **quantity_change**: 正数为入库，负数为出库
    - **transaction_type**: 变动类型(采购入库、销售出库、调拨等)
    """
    service = InventoryService(db)
    try:
        return await service.adjust_inventory(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{inventory_id}/transactions",
    response_model=List[InventoryTransactionResponse],
    summary="获取库存变动记录"
)
async def get_inventory_transactions(
    inventory_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取某库存记录的变动历史"""
    service = InventoryService(db)
    return await service.get_transactions(inventory_id, skip, limit)
