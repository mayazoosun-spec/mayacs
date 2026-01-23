"""门店和销售渠道数据模型"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class StoreType(str, enum.Enum):
    """门店类型"""
    WAREHOUSE = "warehouse"  # 仓库
    RETAIL_STORE = "retail_store"  # 零售门店
    FLAGSHIP_STORE = "flagship_store"  # 旗舰店


class ChannelType(str, enum.Enum):
    """销售渠道类型"""
    ONLINE_WEBSITE = "online_website"  # 官网商城
    ONLINE_TMALL = "online_tmall"  # 天猫
    ONLINE_JD = "online_jd"  # 京东
    ONLINE_DOUYIN = "online_douyin"  # 抖音
    ONLINE_WECHAT = "online_wechat"  # 微信小程序
    OFFLINE_STORE = "offline_store"  # 线下门店
    OFFLINE_WHOLESALE = "offline_wholesale"  # 批发


class Store(Base):
    """门店/仓库"""
    __tablename__ = "stores"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, comment="门店编码")
    name = Column(String(200), nullable=False, comment="门店名称")
    store_type = Column(Enum(StoreType), default=StoreType.RETAIL_STORE, comment="门店类型")

    # 地址信息
    province = Column(String(50), comment="省份")
    city = Column(String(50), comment="城市")
    district = Column(String(50), comment="区县")
    address = Column(Text, comment="详细地址")

    # 联系信息
    contact_person = Column(String(100), comment="负责人")
    contact_phone = Column(String(20), comment="联系电话")

    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    inventory_records = relationship("Inventory", back_populates="store")
    orders = relationship("Order", back_populates="store")
    sales_channels = relationship("SalesChannel", back_populates="store")


class SalesChannel(Base):
    """销售渠道"""
    __tablename__ = "sales_channels"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, comment="渠道编码")
    name = Column(String(200), nullable=False, comment="渠道名称")
    channel_type = Column(Enum(ChannelType), nullable=False, comment="渠道类型")

    # 关联门店(线下渠道)
    store_id = Column(Integer, ForeignKey("stores.id"), comment="关联门店ID")

    # 渠道配置
    config = Column(Text, comment="渠道配置(JSON)")

    # 状态
    is_active = Column(Boolean, default=True, comment="是否启用")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    store = relationship("Store", back_populates="sales_channels")
    orders = relationship("Order", back_populates="channel")
