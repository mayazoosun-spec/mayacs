"""产品管理API"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.product import ProductService
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductCategoryCreate,
    ProductCategoryUpdate,
    ProductCategoryResponse,
    SupplierCreate,
    SupplierUpdate,
    SupplierResponse,
)
from app.models.product import ProductStatus

router = APIRouter()


# ========== 产品接口 ==========

@router.post("", response_model=ProductResponse, summary="创建产品")
async def create_product(
    data: ProductCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建新产品
    - **product_type**: own(自有产品) / third_party(第三方产品)
    - **sell_online/sell_offline**: 控制产品在线上/线下渠道的销售
    """
    service = ProductService(db)

    # 检查SKU是否已存在
    existing = await service.get_product_by_sku(data.sku)
    if existing:
        raise HTTPException(status_code=400, detail="SKU已存在")

    return await service.create_product(data)


@router.get("", response_model=List[ProductResponse], summary="获取产品列表")
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category_id: Optional[int] = None,
    product_type: Optional[str] = None,
    status: Optional[ProductStatus] = None,
    sell_online: Optional[bool] = None,
    sell_offline: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取产品列表，支持多种筛选条件"""
    service = ProductService(db)
    return await service.get_products(
        skip=skip,
        limit=limit,
        category_id=category_id,
        product_type=product_type,
        status=status,
        sell_online=sell_online,
        sell_offline=sell_offline,
        search=search,
    )


@router.get("/{product_id}", response_model=ProductResponse, summary="获取产品详情")
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个产品详情"""
    service = ProductService(db)
    product = await service.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product


@router.put("/{product_id}", response_model=ProductResponse, summary="更新产品")
async def update_product(
    product_id: int,
    data: ProductUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新产品信息"""
    service = ProductService(db)
    product = await service.update_product(product_id, data)
    if not product:
        raise HTTPException(status_code=404, detail="产品不存在")
    return product


@router.delete("/{product_id}", summary="删除产品")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除产品"""
    service = ProductService(db)
    success = await service.delete_product(product_id)
    if not success:
        raise HTTPException(status_code=404, detail="产品不存在")
    return {"message": "删除成功"}


# ========== 分类接口 ==========

@router.post("/categories", response_model=ProductCategoryResponse, summary="创建分类")
async def create_category(
    data: ProductCategoryCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建产品分类"""
    service = ProductService(db)
    return await service.create_category(data)


@router.get("/categories", response_model=List[ProductCategoryResponse], summary="获取分类列表")
async def get_categories(
    parent_id: Optional[int] = None,
    include_inactive: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """获取产品分类列表"""
    service = ProductService(db)
    return await service.get_categories(parent_id, include_inactive)


@router.put("/categories/{category_id}", response_model=ProductCategoryResponse, summary="更新分类")
async def update_category(
    category_id: int,
    data: ProductCategoryUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新产品分类"""
    service = ProductService(db)
    category = await service.update_category(category_id, data)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


# ========== 供应商接口 ==========

@router.post("/suppliers", response_model=SupplierResponse, summary="创建供应商")
async def create_supplier(
    data: SupplierCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建供应商(第三方产品的供应商)"""
    service = ProductService(db)
    return await service.create_supplier(data)


@router.get("/suppliers", response_model=List[SupplierResponse], summary="获取供应商列表")
async def get_suppliers(
    include_inactive: bool = False,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取供应商列表"""
    service = ProductService(db)
    return await service.get_suppliers(include_inactive, search)


@router.put("/suppliers/{supplier_id}", response_model=SupplierResponse, summary="更新供应商")
async def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新供应商信息"""
    service = ProductService(db)
    supplier = await service.update_supplier(supplier_id, data)
    if not supplier:
        raise HTTPException(status_code=404, detail="供应商不存在")
    return supplier
