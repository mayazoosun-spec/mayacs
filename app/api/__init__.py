"""API路由"""
from fastapi import APIRouter
from app.api import products, inventory, stores, orders

api_router = APIRouter()

api_router.include_router(products.router, prefix="/products", tags=["产品管理"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["库存管理"])
api_router.include_router(stores.router, prefix="/stores", tags=["门店管理"])
api_router.include_router(orders.router, prefix="/orders", tags=["订单管理"])
