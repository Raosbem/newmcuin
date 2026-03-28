import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Numeric, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class OrderStatus(str, enum.Enum):
    RECEIVED   = "received"
    PROCESSING = "processing"
    SHIPPED    = "shipped"
    DELIVERED  = "delivered"
    CANCELLED  = "cancelled"


class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id      = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    status       = Column(Enum(OrderStatus, values_callable=lambda obj: [e.value for e in obj], name="orderstatus", create_type=False), default=OrderStatus.RECEIVED, nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    cancelled_at = Column(DateTime, nullable=True)

    user  = relationship("User", backref="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

    @property
    def customer_name(self) -> str | None:
        return self.user.full_name if self.user else None


class OrderItem(Base):
    __tablename__ = "order_items"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id   = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    part_id    = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    quantity   = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    subtotal   = Column(Numeric(12, 2), nullable=False)

    order = relationship("Order", back_populates="items")
    part  = relationship("Part", backref="order_items")

    @property
    def part_name(self) -> str | None:
        return self.part.name if self.part else None