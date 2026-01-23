"""订单服务"""
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderUpdate


class OrderService:
    """订单服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    def _generate_order_no(self) -> str:
        """生成订单编号"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        unique_id = uuid.uuid4().hex[:6].upper()
        return f"ORD{timestamp}{unique_id}"

    async def create_order(self, data: OrderCreate) -> Order:
        """创建订单"""
        # 生成订单编号
        order_no = self._generate_order_no()

        # 创建订单
        order = Order(
            order_no=order_no,
            channel_id=data.channel_id,
            store_id=data.store_id,
            customer_name=data.customer_name,
            customer_phone=data.customer_phone,
            customer_email=data.customer_email,
            shipping_address=data.shipping_address,
            shipping_name=data.shipping_name,
            shipping_phone=data.shipping_phone,
            payment_method=data.payment_method,
            remark=data.remark,
            subtotal=Decimal("0"),
            discount_amount=Decimal("0"),
            shipping_fee=Decimal("0"),
            total_amount=Decimal("0"),
        )
        self.db.add(order)
        await self.db.flush()

        # 添加订单明细
        subtotal = Decimal("0")
        for item_data in data.items:
            # 获取产品信息
            product = await self.db.execute(
                select(Product).where(Product.id == item_data.product_id)
            )
            product = product.scalar_one_or_none()
            if not product:
                raise ValueError(f"产品不存在: {item_data.product_id}")

            # 计算单价和小计
            unit_price = item_data.unit_price or product.retail_price
            item_subtotal = unit_price * item_data.quantity * item_data.discount_rate / 100

            # 创建订单明细
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                product_sku=product.sku,
                unit_price=unit_price,
                quantity=item_data.quantity,
                discount_rate=item_data.discount_rate,
                subtotal=item_subtotal,
            )
            self.db.add(order_item)
            subtotal += item_subtotal

        # 更新订单金额
        order.subtotal = subtotal
        order.total_amount = subtotal - order.discount_amount + order.shipping_fee

        await self.db.flush()
        await self.db.refresh(order)

        # 加载订单明细
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order.id)
        )
        return result.scalar_one()

    async def get_order(self, order_id: int) -> Optional[Order]:
        """获取订单详情"""
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def get_order_by_no(self, order_no: str) -> Optional[Order]:
        """通过订单号获取订单"""
        result = await self.db.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.order_no == order_no)
        )
        return result.scalar_one_or_none()

    async def get_orders(
        self,
        skip: int = 0,
        limit: int = 20,
        channel_id: Optional[int] = None,
        store_id: Optional[int] = None,
        status: Optional[OrderStatus] = None,
        customer_phone: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[Order]:
        """获取订单列表"""
        query = select(Order)

        if channel_id:
            query = query.where(Order.channel_id == channel_id)
        if store_id:
            query = query.where(Order.store_id == store_id)
        if status:
            query = query.where(Order.status == status)
        if customer_phone:
            query = query.where(Order.customer_phone == customer_phone)
        if start_date:
            query = query.where(Order.created_at >= start_date)
        if end_date:
            query = query.where(Order.created_at <= end_date)

        query = query.order_by(Order.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_order(
        self, order_id: int, data: OrderUpdate
    ) -> Optional[Order]:
        """更新订单"""
        order = await self.get_order(order_id)
        if not order:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(order, key, value)

        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def update_order_status(
        self, order_id: int, status: OrderStatus
    ) -> Optional[Order]:
        """更新订单状态"""
        order = await self.get_order(order_id)
        if not order:
            return None

        order.status = status

        # 如果是已支付状态，记录支付时间
        if status == OrderStatus.PAID:
            order.paid_at = datetime.now()

        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def cancel_order(self, order_id: int) -> Optional[Order]:
        """取消订单"""
        order = await self.get_order(order_id)
        if not order:
            return None

        # 只有待支付和已支付状态可以取消
        if order.status not in [OrderStatus.PENDING, OrderStatus.PAID]:
            raise ValueError("当前订单状态不允许取消")

        order.status = OrderStatus.CANCELLED
        await self.db.flush()
        await self.db.refresh(order)
        return order

    async def get_order_statistics(
        self,
        store_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        """获取订单统计"""
        from sqlalchemy import func

        query = select(
            func.count(Order.id).label("total_orders"),
            func.sum(Order.total_amount).label("total_amount"),
        ).where(Order.status != OrderStatus.CANCELLED)

        if store_id:
            query = query.where(Order.store_id == store_id)
        if channel_id:
            query = query.where(Order.channel_id == channel_id)
        if start_date:
            query = query.where(Order.created_at >= start_date)
        if end_date:
            query = query.where(Order.created_at <= end_date)

        result = await self.db.execute(query)
        row = result.one()

        return {
            "total_orders": row.total_orders or 0,
            "total_amount": float(row.total_amount or 0),
        }
