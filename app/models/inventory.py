"""库存相关数据模型"""
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class TransactionType(str, enum.Enum):
    """库存变动类型"""
    PURCHASE = "purchase"  # 采购入库
    SALE = "sale"  # 销售出库
    RETURN_IN = "return_in"  # 退货入库
    RETURN_OUT = "return_out"  # 退货出库
    TRANSFER_IN = "transfer_in"  # 调拨入库
    TRANSFER_OUT = "transfer_out"  # 调拨出库
    ADJUSTMENT = "adjustment"  # 库存调整
    DAMAGE = "damage"  # 损耗


class Inventory(Base):
    """库存记录"""
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="产品ID")
    store_id = Column(Integer, ForeignKey("stores.id"), nullable=False, comment="门店/仓库ID")

    # 库存数量
    quantity = Column(Integer, default=0, comment="当前库存")
    reserved_quantity = Column(Integer, default=0, comment="预留库存(已下单未出库)")
    available_quantity = Column(Integer, default=0, comment="可用库存")

    # 库存预警
    min_quantity = Column(Integer, default=0, comment="最低库存预警")
    max_quantity = Column(Integer, comment="最高库存预警")

    # 时间戳
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    product = relationship("Product", back_populates="inventory_records")
    store = relationship("Store", back_populates="inventory_records")
    transactions = relationship("InventoryTransaction", back_populates="inventory")


class InventoryTransaction(Base):
    """库存变动记录"""
    __tablename__ = "inventory_transactions"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)

    # 变动信息
    transaction_type = Column(Enum(TransactionType), nullable=False, comment="变动类型")
    quantity_change = Column(Integer, nullable=False, comment="变动数量(正数入库,负数出库)")
    quantity_before = Column(Integer, nullable=False, comment="变动前数量")
    quantity_after = Column(Integer, nullable=False, comment="变动后数量")

    # 关联单据
    reference_type = Column(String(50), comment="关联单据类型")
    reference_id = Column(Integer, comment="关联单据ID")

    # 备注
    remark = Column(Text, comment="备注")

    # 操作人
    operator = Column(String(100), comment="操作人")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    inventory = relationship("Inventory", back_populates="transactions")
