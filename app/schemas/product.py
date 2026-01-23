"""产品相关的Schema定义"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime
from app.models.product import ProductType, ProductStatus


# ========== 产品分类 ==========
class ProductCategoryBase(BaseModel):
    name: str = Field(..., max_length=100, description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    sort_order: int = Field(0, description="排序")


class ProductCategoryCreate(ProductCategoryBase):
    pass


class ProductCategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class ProductCategoryResponse(ProductCategoryBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 供应商 ==========
class SupplierBase(BaseModel):
    name: str = Field(..., max_length=200, description="供应商名称")
    code: Optional[str] = Field(None, max_length=50, description="供应商编码")
    contact_person: Optional[str] = Field(None, max_length=100, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    contact_email: Optional[str] = Field(None, max_length=100, description="联系邮箱")
    address: Optional[str] = Field(None, description="地址")


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    contact_person: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None


class SupplierResponse(SupplierBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ========== 产品 ==========
class ProductBase(BaseModel):
    sku: str = Field(..., max_length=50, description="SKU编码")
    barcode: Optional[str] = Field(None, max_length=50, description="条形码")
    name: str = Field(..., max_length=200, description="产品名称")
    description: Optional[str] = Field(None, description="产品描述")
    product_type: ProductType = Field(ProductType.OWN, description="产品类型")
    category_id: Optional[int] = Field(None, description="分类ID")
    supplier_id: Optional[int] = Field(None, description="供应商ID")
    cost_price: Optional[Decimal] = Field(None, ge=0, description="成本价")
    retail_price: Decimal = Field(..., ge=0, description="零售价")
    wholesale_price: Optional[Decimal] = Field(None, ge=0, description="批发价")
    unit: str = Field("件", max_length=20, description="单位")
    weight: Optional[Decimal] = Field(None, ge=0, description="重量(kg)")
    specifications: Optional[str] = Field(None, description="规格参数(JSON)")
    sell_online: bool = Field(True, description="是否线上销售")
    sell_offline: bool = Field(True, description="是否线下销售")


class ProductCreate(ProductBase):
    status: ProductStatus = Field(ProductStatus.DRAFT, description="产品状态")


class ProductUpdate(BaseModel):
    sku: Optional[str] = Field(None, max_length=50)
    barcode: Optional[str] = Field(None, max_length=50)
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    product_type: Optional[ProductType] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None
    cost_price: Optional[Decimal] = None
    retail_price: Optional[Decimal] = None
    wholesale_price: Optional[Decimal] = None
    unit: Optional[str] = None
    weight: Optional[Decimal] = None
    specifications: Optional[str] = None
    status: Optional[ProductStatus] = None
    sell_online: Optional[bool] = None
    sell_offline: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    status: ProductStatus
    created_at: datetime
    updated_at: Optional[datetime]
    category: Optional[ProductCategoryResponse] = None
    supplier: Optional[SupplierResponse] = None

    class Config:
        from_attributes = True
