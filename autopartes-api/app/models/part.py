import uuid
from sqlalchemy import Column, String, Integer, Numeric, Boolean, Text
from sqlalchemy.dialects.postgresql import UUID
from app.models.base import Base, TimestampMixin


class Part(Base, TimestampMixin):
    __tablename__ = "parts"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku            = Column(String(100), unique=True, nullable=False, index=True)
    name           = Column(String(255), nullable=False)
    description    = Column(Text, nullable=True)
    brand          = Column(String(100), nullable=True)
    category       = Column(String(100), nullable=True, index=True)
    price          = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    is_active      = Column(Boolean, default=True, nullable=False)