# app/models/inventory_log.py
import enum
from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
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
    action_type     = Column(Enum(InventoryAction), nullable=False)
    quantity_before = Column(Integer, nullable=False)
    quantity_after  = Column(Integer, nullable=False)
    delta           = Column(Integer, nullable=False)
    reason          = Column(Text)

    part       = relationship("Part", back_populates="inventory_logs")
    managed_by = relationship("User", back_populates="inventory_logs")

class StatusHistory(Base):
    __tablename__ = "status_history"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id    = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    changed_by  = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    old_status  = Column(String(50))
    new_status  = Column(String(50), nullable=False)
    notes       = Column(Text)
    changed_at  = Column(DateTime, default=datetime.utcnow, nullable=False)

    order            = relationship("Order", back_populates="status_history")
    changed_by_user  = relationship("User", back_populates="status_changes")