from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem, OrderStatus
from app.models.inventory_log import StatusHistory
from app.repositories.order_repo import OrderRepository
from app.repositories.part_repo import PartRepository
from app.schemas.order import OrderCreateSchema

class OrderService:
    def __init__(self, db: Session):
        self.db         = db
        self.order_repo = OrderRepository(db)
        self.part_repo  = PartRepository(db)

    def create_order(self, user_id: str, payload: OrderCreateSchema) -> Order:
        items = []
        total = 0

        for line in payload.items:
            part = self.part_repo.get_by_id(line.part_id)
            if not part or not part.is_active:
                raise ValueError(f"Autoparte {line.part_id} no encontrada")
            if part.stock_quantity < line.quantity:
                raise ValueError(f"Stock insuficiente para {part.name}")

            subtotal = part.price * line.quantity
            total += subtotal
            items.append(OrderItem(
                part_id    = part.id,
                quantity   = line.quantity,
                unit_price = part.price,
                subtotal   = subtotal,
            ))

        order = Order(
            user_id      = user_id,
            status       = OrderStatus.RECEIVED,
            total_amount = total,
            items        = items,
        )
        self.order_repo.create(order)

        # Descontar stock transaccionalmente
        for line in payload.items:
            self.part_repo.decrement_stock(line.part_id, line.quantity)

        self.db.commit()
        self.db.refresh(order)
        return order

    def cancel_order(self, order_id: str, user_id: str, is_staff: bool) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Pedido no encontrado")
        if not is_staff and str(order.user_id) != user_id:
            raise PermissionError("No puedes cancelar este pedido")
        if order.status in (OrderStatus.SHIPPED, OrderStatus.CANCELLED):
            raise ValueError(f"No se puede cancelar un pedido en estado {order.status}")

        order.status       = OrderStatus.CANCELLED
        order.cancelled_at = datetime.now(timezone.utc)
        self.db.commit()
        return order

    def change_status(self, order_id: str, new_status: OrderStatus,
                      changed_by: str, notes: str = None) -> Order:
        order = self.order_repo.get_by_id(order_id)
        if not order:
            raise ValueError("Pedido no encontrado")

        history = StatusHistory(
            order_id   = order.id,
            changed_by = changed_by,
            old_status = order.status,
            new_status = new_status,
            notes      = notes,
        )
        order.status = new_status
        self.db.add(history)
        self.db.commit()
        return order