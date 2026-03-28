import uuid
from sqlalchemy import Column, String, Integer, Numeric, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import Base, TimestampMixin


class Part(Base, TimestampMixin):
    __tablename__ = "parts"

    id             = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku            = Column(String(100), unique=True, nullable=False, index=True)
    name           = Column(String(255), nullable=False)
    description    = Column(Text, nullable=True)
    brand_id       = Column(UUID(as_uuid=True), ForeignKey("brands.id"), nullable=True)
    category_id    = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    price          = Column(Numeric(10, 2), nullable=False)
    stock_quantity = Column(Integer, default=0, nullable=False)
    is_active      = Column(Boolean, default=True, nullable=False)
    image_url      = Column(String(500), nullable=True)

    brand_rel    = relationship("Brand",    back_populates="parts")
    category_rel = relationship("Category", back_populates="parts")

    @property
    def brand(self) -> str | None:
        return self.brand_rel.name if self.brand_rel else None

    @property
    def category(self) -> str | None:
        return self.category_rel.name if self.category_rel else None
