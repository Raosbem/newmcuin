import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class InventoryAction(str, enum.Enum):
    RESTOCK    = "restock"
    ADJUSTMENT = "adjustment"
    SALE       = "sale"
    RETURN     = "return"


class InventoryLog(Base, TimestampMixin):
    __tablename__ = "inventory_logs"

    id              = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    part_id         = Column(UUID(as_uuid=True), ForeignKey("parts.id"), nullable=False)
    user_id         = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    action_type     = Column(Enum(InventoryAction, values_callable=lambda obj: [e.value for e in obj], name="inventoryaction", create_type=False), nullable=False)
    quantity_before = Column(Integer, nullable=False)
    quantity_after  = Column(Integer, nullable=False)
    delta           = Column(Integer, nullable=False)
    reason          = Column(Text)

    # backref crea automáticamente Part.inventory_logs y User.inventory_logs
    # sin necesitar definir el lado inverso en esos modelos
    part       = relationship("Part", backref="inventory_logs")
    managed_by = relationship("User", backref="inventory_logs")

    @property
    def part_name(self) -> str | None:
        return self.part.name if self.part else None


class StatusHistory(Base):
    __tablename__ = "status_history"

    id         = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id   = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    old_status = Column(String(50))
    new_status = Column(String(50), nullable=False)
    notes      = Column(Text)
    changed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)

    # backref crea automáticamente Order.status_history y User.status_changes
    order           = relationship("Order", backref="status_history")
    changed_by_user = relationship("User", backref="status_changes")
