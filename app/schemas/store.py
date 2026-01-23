"""门店和销售渠道的Schema定义"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.store import StoreType, ChannelType


# ========== 门店 ==========
class StoreBase(BaseModel):
    code: str = Field(..., max_length=50, description="门店编码")
    name: str = Field(..., max_length=200, description="门店名称")
    store_type: StoreType = Field(StoreType.RETAIL_STORE, description="门店类型")
    province: Optional[str] = Field(None, max_length=50, description="省份")
    city: Optional[str] = Field(None, max_length=50, description="城市")
    district: Optional[str] = Field(None, max_length=50, description="区县")
    address: Optional[str] = Field(None, description="详细地址")
    contact_person: Optional[str] = Field(None, max_length=100, description="负责人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")


class StoreCreate(StoreBase):
    pass


class StoreUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=200)
    store_type: Optional[StoreType] = None
    province: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: Optional[bool] = None


class StoreResponse(StoreBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ========== 销售渠道 ==========
class SalesChannelBase(BaseModel):
    code: str = Field(..., max_length=50, description="渠道编码")
    name: str = Field(..., max_length=200, description="渠道名称")
    channel_type: ChannelType = Field(..., description="渠道类型")
    store_id: Optional[int] = Field(None, description="关联门店ID")
    config: Optional[str] = Field(None, description="渠道配置(JSON)")


class SalesChannelCreate(SalesChannelBase):
    pass


class SalesChannelUpdate(BaseModel):
    code: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=200)
    channel_type: Optional[ChannelType] = None
    store_id: Optional[int] = None
    config: Optional[str] = None
    is_active: Optional[bool] = None


class SalesChannelResponse(SalesChannelBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
