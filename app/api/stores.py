"""门店和渠道管理API"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.store import StoreService
from app.schemas.store import (
    StoreCreate,
    StoreUpdate,
    StoreResponse,
    SalesChannelCreate,
    SalesChannelUpdate,
    SalesChannelResponse,
)
from app.models.store import StoreType, ChannelType

router = APIRouter()


# ========== 门店接口 ==========

@router.post("", response_model=StoreResponse, summary="创建门店")
async def create_store(
    data: StoreCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建门店/仓库
    - **store_type**: warehouse(仓库) / retail_store(零售门店) / flagship_store(旗舰店)
    """
    service = StoreService(db)

    # 检查编码是否已存在
    existing = await service.get_store_by_code(data.code)
    if existing:
        raise HTTPException(status_code=400, detail="门店编码已存在")

    return await service.create_store(data)


@router.get("", response_model=List[StoreResponse], summary="获取门店列表")
async def get_stores(
    store_type: Optional[StoreType] = None,
    city: Optional[str] = None,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """获取门店列表，支持按类型、城市筛选"""
    service = StoreService(db)
    return await service.get_stores(
        store_type=store_type,
        city=city,
        include_inactive=include_inactive,
    )


@router.get("/{store_id}", response_model=StoreResponse, summary="获取门店详情")
async def get_store(
    store_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个门店详情"""
    service = StoreService(db)
    store = await service.get_store(store_id)
    if not store:
        raise HTTPException(status_code=404, detail="门店不存在")
    return store


@router.put("/{store_id}", response_model=StoreResponse, summary="更新门店")
async def update_store(
    store_id: int,
    data: StoreUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新门店信息"""
    service = StoreService(db)
    store = await service.update_store(store_id, data)
    if not store:
        raise HTTPException(status_code=404, detail="门店不存在")
    return store


@router.delete("/{store_id}", summary="删除门店")
async def delete_store(
    store_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除门店(软删除)"""
    service = StoreService(db)
    success = await service.delete_store(store_id)
    if not success:
        raise HTTPException(status_code=404, detail="门店不存在")
    return {"message": "删除成功"}


# ========== 销售渠道接口 ==========

@router.post("/channels", response_model=SalesChannelResponse, summary="创建销售渠道")
async def create_channel(
    data: SalesChannelCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建销售渠道

    线上渠道类型:
    - online_website: 官网商城
    - online_tmall: 天猫
    - online_jd: 京东
    - online_douyin: 抖音
    - online_wechat: 微信小程序

    线下渠道类型:
    - offline_store: 线下门店
    - offline_wholesale: 批发
    """
    service = StoreService(db)

    # 检查编码是否已存在
    existing = await service.get_channel_by_code(data.code)
    if existing:
        raise HTTPException(status_code=400, detail="渠道编码已存在")

    return await service.create_channel(data)


@router.get("/channels", response_model=List[SalesChannelResponse], summary="获取渠道列表")
async def get_channels(
    channel_type: Optional[ChannelType] = None,
    store_id: Optional[int] = None,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """获取销售渠道列表"""
    service = StoreService(db)
    return await service.get_channels(
        channel_type=channel_type,
        store_id=store_id,
        include_inactive=include_inactive,
    )


@router.get("/channels/online", response_model=List[SalesChannelResponse], summary="获取线上渠道")
async def get_online_channels(
    db: AsyncSession = Depends(get_db)
):
    """获取所有线上销售渠道"""
    service = StoreService(db)
    return await service.get_online_channels()


@router.get("/channels/offline", response_model=List[SalesChannelResponse], summary="获取线下渠道")
async def get_offline_channels(
    db: AsyncSession = Depends(get_db)
):
    """获取所有线下销售渠道"""
    service = StoreService(db)
    return await service.get_offline_channels()


@router.get("/channels/{channel_id}", response_model=SalesChannelResponse, summary="获取渠道详情")
async def get_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个销售渠道详情"""
    service = StoreService(db)
    channel = await service.get_channel(channel_id)
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")
    return channel


@router.put("/channels/{channel_id}", response_model=SalesChannelResponse, summary="更新渠道")
async def update_channel(
    channel_id: int,
    data: SalesChannelUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新销售渠道"""
    service = StoreService(db)
    channel = await service.update_channel(channel_id, data)
    if not channel:
        raise HTTPException(status_code=404, detail="渠道不存在")
    return channel


@router.delete("/channels/{channel_id}", summary="删除渠道")
async def delete_channel(
    channel_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除销售渠道(软删除)"""
    service = StoreService(db)
    success = await service.delete_channel(channel_id)
    if not success:
        raise HTTPException(status_code=404, detail="渠道不存在")
    return {"message": "删除成功"}
