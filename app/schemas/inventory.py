"""库存相关的Schema定义"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.inventory import TransactionType


class InventoryBase(BaseModel):
    product_id: int = Field(..., description="产品ID")
    store_id: int = Field(..., description="门店/仓库ID")
    quantity: int = Field(0, ge=0, description="当前库存")
    min_quantity: int = Field(0, ge=0, description="最低库存预警")
    max_quantity: Optional[int] = Field(None, description="最高库存预警")


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    reserved_quantity: Optional[int] = Field(None, ge=0)
    min_quantity: Optional[int] = Field(None, ge=0)
    max_quantity: Optional[int] = None


class InventoryResponse(InventoryBase):
    id: int
    reserved_quantity: int
    available_quantity: int
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class InventoryTransactionCreate(BaseModel):
    inventory_id: int = Field(..., description="库存记录ID")
    transaction_type: TransactionType = Field(..., description="变动类型")
    quantity_change: int = Field(..., description="变动数量")
    reference_type: Optional[str] = Field(None, max_length=50, description="关联单据类型")
    reference_id: Optional[int] = Field(None, description="关联单据ID")
    remark: Optional[str] = Field(None, description="备注")
    operator: Optional[str] = Field(None, max_length=100, description="操作人")


class InventoryTransactionResponse(BaseModel):
    id: int
    inventory_id: int
    transaction_type: TransactionType
    quantity_change: int
    quantity_before: int
    quantity_after: int
    reference_type: Optional[str]
    reference_id: Optional[int]
    remark: Optional[str]
    operator: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
