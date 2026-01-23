"""订单相关的Schema定义"""
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from app.models.order import OrderStatus, PaymentMethod


# ========== 订单明细 ==========
class OrderItemBase(BaseModel):
    product_id: int = Field(..., description="产品ID")
    quantity: int = Field(..., gt=0, description="数量")
    unit_price: Optional[Decimal] = Field(None, ge=0, description="单价(不填则使用产品零售价)")
    discount_rate: Decimal = Field(100, ge=0, le=100, description="折扣率(百分比)")


class OrderItemCreate(OrderItemBase):
    pass


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_sku: Optional[str]
    unit_price: Decimal
    quantity: int
    discount_rate: Decimal
    subtotal: Decimal

    class Config:
        from_attributes = True


# ========== 订单 ==========
class OrderBase(BaseModel):
    channel_id: Optional[int] = Field(None, description="销售渠道ID")
    store_id: Optional[int] = Field(None, description="门店ID")
    customer_name: Optional[str] = Field(None, max_length=100, description="客户姓名")
    customer_phone: Optional[str] = Field(None, max_length=20, description="客户电话")
    customer_email: Optional[str] = Field(None, max_length=100, description="客户邮箱")
    shipping_address: Optional[str] = Field(None, description="收货地址")
    shipping_name: Optional[str] = Field(None, max_length=100, description="收货人")
    shipping_phone: Optional[str] = Field(None, max_length=20, description="收货电话")
    remark: Optional[str] = Field(None, description="订单备注")


class OrderCreate(OrderBase):
    items: List[OrderItemCreate] = Field(..., min_length=1, description="订单明细")
    payment_method: Optional[PaymentMethod] = Field(None, description="支付方式")


class OrderUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_email: Optional[str] = None
    shipping_address: Optional[str] = None
    shipping_name: Optional[str] = None
    shipping_phone: Optional[str] = None
    status: Optional[OrderStatus] = None
    payment_method: Optional[PaymentMethod] = None
    remark: Optional[str] = None
    internal_note: Optional[str] = None


class OrderResponse(OrderBase):
    id: int
    order_no: str
    subtotal: Decimal
    discount_amount: Decimal
    shipping_fee: Decimal
    total_amount: Decimal
    payment_method: Optional[PaymentMethod]
    paid_at: Optional[datetime]
    status: OrderStatus
    internal_note: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class OrderListResponse(BaseModel):
    """订单列表响应(不包含明细)"""
    id: int
    order_no: str
    channel_id: Optional[int]
    store_id: Optional[int]
    customer_name: Optional[str]
    total_amount: Decimal
    status: OrderStatus
    created_at: datetime

    class Config:
        from_attributes = True
