"""门店和渠道服务"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.store import Store, SalesChannel, StoreType, ChannelType
from app.schemas.store import (
    StoreCreate,
    StoreUpdate,
    SalesChannelCreate,
    SalesChannelUpdate,
)


class StoreService:
    """门店和渠道服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========== 门店操作 ==========

    async def create_store(self, data: StoreCreate) -> Store:
        """创建门店"""
        store = Store(**data.model_dump())
        self.db.add(store)
        await self.db.flush()
        await self.db.refresh(store)
        return store

    async def get_store(self, store_id: int) -> Optional[Store]:
        """获取门店"""
        result = await self.db.execute(
            select(Store).where(Store.id == store_id)
        )
        return result.scalar_one_or_none()

    async def get_store_by_code(self, code: str) -> Optional[Store]:
        """通过编码获取门店"""
        result = await self.db.execute(
            select(Store).where(Store.code == code)
        )
        return result.scalar_one_or_none()

    async def get_stores(
        self,
        store_type: Optional[StoreType] = None,
        city: Optional[str] = None,
        include_inactive: bool = False,
    ) -> List[Store]:
        """获取门店列表"""
        query = select(Store)

        if store_type:
            query = query.where(Store.store_type == store_type)
        if city:
            query = query.where(Store.city == city)
        if not include_inactive:
            query = query.where(Store.is_active == True)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_store(
        self, store_id: int, data: StoreUpdate
    ) -> Optional[Store]:
        """更新门店"""
        store = await self.get_store(store_id)
        if not store:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(store, key, value)

        await self.db.flush()
        await self.db.refresh(store)
        return store

    async def delete_store(self, store_id: int) -> bool:
        """删除门店(软删除)"""
        store = await self.get_store(store_id)
        if not store:
            return False
        store.is_active = False
        await self.db.flush()
        return True

    # ========== 销售渠道操作 ==========

    async def create_channel(self, data: SalesChannelCreate) -> SalesChannel:
        """创建销售渠道"""
        channel = SalesChannel(**data.model_dump())
        self.db.add(channel)
        await self.db.flush()
        await self.db.refresh(channel)
        return channel

    async def get_channel(self, channel_id: int) -> Optional[SalesChannel]:
        """获取销售渠道"""
        result = await self.db.execute(
            select(SalesChannel).where(SalesChannel.id == channel_id)
        )
        return result.scalar_one_or_none()

    async def get_channel_by_code(self, code: str) -> Optional[SalesChannel]:
        """通过编码获取渠道"""
        result = await self.db.execute(
            select(SalesChannel).where(SalesChannel.code == code)
        )
        return result.scalar_one_or_none()

    async def get_channels(
        self,
        channel_type: Optional[ChannelType] = None,
        store_id: Optional[int] = None,
        include_inactive: bool = False,
    ) -> List[SalesChannel]:
        """获取销售渠道列表"""
        query = select(SalesChannel)

        if channel_type:
            query = query.where(SalesChannel.channel_type == channel_type)
        if store_id:
            query = query.where(SalesChannel.store_id == store_id)
        if not include_inactive:
            query = query.where(SalesChannel.is_active == True)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_online_channels(self) -> List[SalesChannel]:
        """获取线上渠道"""
        result = await self.db.execute(
            select(SalesChannel).where(
                SalesChannel.channel_type.in_([
                    ChannelType.ONLINE_WEBSITE,
                    ChannelType.ONLINE_TMALL,
                    ChannelType.ONLINE_JD,
                    ChannelType.ONLINE_DOUYIN,
                    ChannelType.ONLINE_WECHAT,
                ]),
                SalesChannel.is_active == True
            )
        )
        return list(result.scalars().all())

    async def get_offline_channels(self) -> List[SalesChannel]:
        """获取线下渠道"""
        result = await self.db.execute(
            select(SalesChannel).where(
                SalesChannel.channel_type.in_([
                    ChannelType.OFFLINE_STORE,
                    ChannelType.OFFLINE_WHOLESALE,
                ]),
                SalesChannel.is_active == True
            )
        )
        return list(result.scalars().all())

    async def update_channel(
        self, channel_id: int, data: SalesChannelUpdate
    ) -> Optional[SalesChannel]:
        """更新销售渠道"""
        channel = await self.get_channel(channel_id)
        if not channel:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(channel, key, value)

        await self.db.flush()
        await self.db.refresh(channel)
        return channel

    async def delete_channel(self, channel_id: int) -> bool:
        """删除销售渠道(软删除)"""
        channel = await self.get_channel(channel_id)
        if not channel:
            return False
        channel.is_active = False
        await self.db.flush()
        return True
