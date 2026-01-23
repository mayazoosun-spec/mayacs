"""产品相关数据模型"""
from sqlalchemy import Column, Integer, String, Text, Numeric, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class ProductType(str, enum.Enum):
    """产品类型"""
    OWN = "own"  # 自有产品
    THIRD_PARTY = "third_party"  # 第三方产品


class ProductStatus(str, enum.Enum):
    """产品状态"""
    DRAFT = "draft"  # 草稿
    ACTIVE = "active"  # 上架
    INACTIVE = "inactive"  # 下架
    DISCONTINUED = "discontinued"  # 停产


class ProductCategory(Base):
    """产品分类"""
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment="分类名称")
    description = Column(Text, comment="分类描述")
    parent_id = Column(Integer, ForeignKey("product_categories.id"), comment="父分类ID")
    sort_order = Column(Integer, default=0, comment="排序")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    parent = relationship("ProductCategory", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")


class Supplier(Base):
    """供应商"""
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="供应商名称")
    code = Column(String(50), unique=True, comment="供应商编码")
    contact_person = Column(String(100), comment="联系人")
    contact_phone = Column(String(20), comment="联系电话")
    contact_email = Column(String(100), comment="联系邮箱")
    address = Column(Text, comment="地址")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    products = relationship("Product", back_populates="supplier")


class Product(Base):
    """产品"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(50), unique=True, nullable=False, comment="SKU编码")
    barcode = Column(String(50), comment="条形码")
    name = Column(String(200), nullable=False, comment="产品名称")
    description = Column(Text, comment="产品描述")

    # 产品类型：自有/第三方
    product_type = Column(
        Enum(ProductType),
        default=ProductType.OWN,
        comment="产品类型：own-自有产品, third_party-第三方产品"
    )

    # 分类和供应商
    category_id = Column(Integer, ForeignKey("product_categories.id"), comment="分类ID")
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), comment="供应商ID")

    # 价格信息
    cost_price = Column(Numeric(10, 2), comment="成本价")
    retail_price = Column(Numeric(10, 2), nullable=False, comment="零售价")
    wholesale_price = Column(Numeric(10, 2), comment="批发价")

    # 产品属性
    unit = Column(String(20), default="件", comment="单位")
    weight = Column(Numeric(10, 3), comment="重量(kg)")
    specifications = Column(Text, comment="规格参数(JSON)")

    # 状态
    status = Column(
        Enum(ProductStatus),
        default=ProductStatus.DRAFT,
        comment="产品状态"
    )

    # 线上/线下销售标记
    sell_online = Column(Boolean, default=True, comment="是否线上销售")
    sell_offline = Column(Boolean, default=True, comment="是否线下销售")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    category = relationship("ProductCategory", back_populates="products")
    supplier = relationship("Supplier", back_populates="products")
    inventory_records = relationship("Inventory", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")
