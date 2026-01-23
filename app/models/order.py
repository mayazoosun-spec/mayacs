"""订单相关数据模型"""
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    """订单状态"""
    PENDING = "pending"  # 待支付
    PAID = "paid"  # 已支付
    PROCESSING = "processing"  # 处理中
    SHIPPED = "shipped"  # 已发货
    DELIVERED = "delivered"  # 已送达
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消
    REFUNDED = "refunded"  # 已退款


class PaymentMethod(str, enum.Enum):
    """支付方式"""
    CASH = "cash"  # 现金
    ALIPAY = "alipay"  # 支付宝
    WECHAT = "wechat"  # 微信支付
    CARD = "card"  # 银行卡
    CREDIT = "credit"  # 赊账


class Order(Base):
    """订单"""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False, comment="订单编号")

    # 渠道和门店
    channel_id = Column(Integer, ForeignKey("sales_channels.id"), comment="销售渠道ID")
    store_id = Column(Integer, ForeignKey("stores.id"), comment="门店ID")

    # 客户信息
    customer_name = Column(String(100), comment="客户姓名")
    customer_phone = Column(String(20), comment="客户电话")
    customer_email = Column(String(100), comment="客户邮箱")

    # 收货信息
    shipping_address = Column(Text, comment="收货地址")
    shipping_name = Column(String(100), comment="收货人")
    shipping_phone = Column(String(20), comment="收货电话")

    # 金额信息
    subtotal = Column(Numeric(12, 2), default=0, comment="商品小计")
    discount_amount = Column(Numeric(12, 2), default=0, comment="优惠金额")
    shipping_fee = Column(Numeric(10, 2), default=0, comment="运费")
    total_amount = Column(Numeric(12, 2), nullable=False, comment="订单总额")

    # 支付信息
    payment_method = Column(Enum(PaymentMethod), comment="支付方式")
    paid_at = Column(DateTime(timezone=True), comment="支付时间")

    # 订单状态
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, comment="订单状态")

    # 备注
    remark = Column(Text, comment="订单备注")
    internal_note = Column(Text, comment="内部备注")

    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    channel = relationship("SalesChannel", back_populates="orders")
    store = relationship("Store", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """订单明细"""
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, comment="订单ID")
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, comment="产品ID")

    # 产品快照(下单时的产品信息)
    product_name = Column(String(200), nullable=False, comment="产品名称")
    product_sku = Column(String(50), comment="产品SKU")

    # 价格和数量
    unit_price = Column(Numeric(10, 2), nullable=False, comment="单价")
    quantity = Column(Integer, nullable=False, comment="数量")
    discount_rate = Column(Numeric(5, 2), default=100, comment="折扣率(百分比)")
    subtotal = Column(Numeric(12, 2), nullable=False, comment="小计")

    # 关系
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
