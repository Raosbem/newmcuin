from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.order import Order, OrderItem

class OrderRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, order: Order) -> Order:
        self.db.add(order)
        self.db.flush()   # obtiene el ID sin commit
        return order

    def get_by_id(self, order_id: str) -> Order | None:
        return self.db.get(Order, order_id)

    def get_by_user(self, user_id: str, skip=0, limit=20) -> list[Order]:
        stmt = (select(Order)
                .where(Order.user_id == user_id)
                .order_by(Order.created_at.desc())
                .offset(skip).limit(limit))
        return self.db.scalars(stmt).all()

    def get_all(self, status=None, skip=0, limit=50) -> list[Order]:
        stmt = select(Order).order_by(Order.created_at.desc())
        if status:
            stmt = stmt.where(Order.status == status)
        return self.db.scalars(stmt.offset(skip).limit(limit)).all()