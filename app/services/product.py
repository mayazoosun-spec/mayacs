"""产品服务"""
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.product import Product, ProductCategory, Supplier, ProductStatus
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductCategoryCreate,
    ProductCategoryUpdate,
    SupplierCreate,
    SupplierUpdate,
)


class ProductService:
    """产品服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    # ========== 产品操作 ==========

    async def create_product(self, data: ProductCreate) -> Product:
        """创建产品"""
        product = Product(**data.model_dump())
        self.db.add(product)
        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def get_product(self, product_id: int) -> Optional[Product]:
        """获取单个产品"""
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.category), selectinload(Product.supplier))
            .where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_product_by_sku(self, sku: str) -> Optional[Product]:
        """通过SKU获取产品"""
        result = await self.db.execute(
            select(Product).where(Product.sku == sku)
        )
        return result.scalar_one_or_none()

    async def get_products(
        self,
        skip: int = 0,
        limit: int = 20,
        category_id: Optional[int] = None,
        product_type: Optional[str] = None,
        status: Optional[ProductStatus] = None,
        sell_online: Optional[bool] = None,
        sell_offline: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[Product]:
        """获取产品列表"""
        query = select(Product).options(
            selectinload(Product.category),
            selectinload(Product.supplier)
        )

        if category_id:
            query = query.where(Product.category_id == category_id)
        if product_type:
            query = query.where(Product.product_type == product_type)
        if status:
            query = query.where(Product.status == status)
        if sell_online is not None:
            query = query.where(Product.sell_online == sell_online)
        if sell_offline is not None:
            query = query.where(Product.sell_offline == sell_offline)
        if search:
            query = query.where(
                Product.name.ilike(f"%{search}%") |
                Product.sku.ilike(f"%{search}%")
            )

        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_product(
        self, product_id: int, data: ProductUpdate
    ) -> Optional[Product]:
        """更新产品"""
        product = await self.get_product(product_id)
        if not product:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        await self.db.flush()
        await self.db.refresh(product)
        return product

    async def delete_product(self, product_id: int) -> bool:
        """删除产品"""
        product = await self.get_product(product_id)
        if not product:
            return False
        await self.db.delete(product)
        return True

    # ========== 分类操作 ==========

    async def create_category(self, data: ProductCategoryCreate) -> ProductCategory:
        """创建分类"""
        category = ProductCategory(**data.model_dump())
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category

    async def get_category(self, category_id: int) -> Optional[ProductCategory]:
        """获取单个分类"""
        result = await self.db.execute(
            select(ProductCategory).where(ProductCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_categories(
        self, parent_id: Optional[int] = None, include_inactive: bool = False
    ) -> List[ProductCategory]:
        """获取分类列表"""
        query = select(ProductCategory)
        if parent_id is not None:
            query = query.where(ProductCategory.parent_id == parent_id)
        if not include_inactive:
            query = query.where(ProductCategory.is_active == True)
        query = query.order_by(ProductCategory.sort_order)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_category(
        self, category_id: int, data: ProductCategoryUpdate
    ) -> Optional[ProductCategory]:
        """更新分类"""
        category = await self.get_category(category_id)
        if not category:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category, key, value)

        await self.db.flush()
        await self.db.refresh(category)
        return category

    # ========== 供应商操作 ==========

    async def create_supplier(self, data: SupplierCreate) -> Supplier:
        """创建供应商"""
        supplier = Supplier(**data.model_dump())
        self.db.add(supplier)
        await self.db.flush()
        await self.db.refresh(supplier)
        return supplier

    async def get_supplier(self, supplier_id: int) -> Optional[Supplier]:
        """获取单个供应商"""
        result = await self.db.execute(
            select(Supplier).where(Supplier.id == supplier_id)
        )
        return result.scalar_one_or_none()

    async def get_suppliers(
        self, include_inactive: bool = False, search: Optional[str] = None
    ) -> List[Supplier]:
        """获取供应商列表"""
        query = select(Supplier)
        if not include_inactive:
            query = query.where(Supplier.is_active == True)
        if search:
            query = query.where(Supplier.name.ilike(f"%{search}%"))
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_supplier(
        self, supplier_id: int, data: SupplierUpdate
    ) -> Optional[Supplier]:
        """更新供应商"""
        supplier = await self.get_supplier(supplier_id)
        if not supplier:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(supplier, key, value)

        await self.db.flush()
        await self.db.refresh(supplier)
        return supplier
