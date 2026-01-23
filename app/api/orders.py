"""订单管理API"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.order import OrderService
from app.schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderListResponse,
)
from app.models.order import OrderStatus

router = APIRouter()


@router.post("", response_model=OrderResponse, summary="创建订单")
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建订单
    - 支持线上和线下订单
    - 通过 channel_id 指定销售渠道
    - 通过 store_id 指定门店(线下订单)
    """
    service = OrderService(db)
    try:
        return await service.create_order(data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=List[OrderListResponse], summary="获取订单列表")
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    channel_id: Optional[int] = None,
    store_id: Optional[int] = None,
    status: Optional[OrderStatus] = None,
    customer_phone: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取订单列表，支持多种筛选条件"""
    service = OrderService(db)
    return await service.get_orders(
        skip=skip,
        limit=limit,
        channel_id=channel_id,
        store_id=store_id,
        status=status,
        customer_phone=customer_phone,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/statistics", summary="获取订单统计")
async def get_order_statistics(
    store_id: Optional[int] = None,
    channel_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取订单统计数据"""
    service = OrderService(db)
    return await service.get_order_statistics(
        store_id=store_id,
        channel_id=channel_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/{order_id}", response_model=OrderResponse, summary="获取订单详情")
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个订单详情(含订单明细)"""
    service = OrderService(db)
    order = await service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.get("/no/{order_no}", response_model=OrderResponse, summary="通过订单号获取订单")
async def get_order_by_no(
    order_no: str,
    db: AsyncSession = Depends(get_db)
):
    """通过订单号获取订单详情"""
    service = OrderService(db)
    order = await service.get_order_by_no(order_no)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.put("/{order_id}", response_model=OrderResponse, summary="更新订单")
async def update_order(
    order_id: int,
    data: OrderUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新订单信息"""
    service = OrderService(db)
    order = await service.update_order(order_id, data)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.put("/{order_id}/status", response_model=OrderResponse, summary="更新订单状态")
async def update_order_status(
    order_id: int,
    status: OrderStatus,
    db: AsyncSession = Depends(get_db)
):
    """
    更新订单状态

    状态流转:
    - pending(待支付) -> paid(已支付) -> processing(处理中) -> shipped(已发货) -> delivered(已送达) -> completed(已完成)
    - 任意状态 -> cancelled(已取消) / refunded(已退款)
    """
    service = OrderService(db)
    order = await service.update_order_status(order_id, status)
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order


@router.post("/{order_id}/cancel", response_model=OrderResponse, summary="取消订单")
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    """取消订单(仅待支付和已支付状态可取消)"""
    service = OrderService(db)
    try:
        order = await service.cancel_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="订单不存在")
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
