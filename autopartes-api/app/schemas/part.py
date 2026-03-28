from pydantic import BaseModel, field_validator
from typing import Optional
from uuid import UUID
from decimal import Decimal


class PartCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    brand_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    price: Decimal
    stock_quantity: int = 0

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v

    @field_validator("stock_quantity")
    @classmethod
    def stock_not_negative(cls, v):
        if v < 0:
            raise ValueError("El stock no puede ser negativo")
        return v


class PartUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    brand_id: Optional[UUID] = None
    category_id: Optional[UUID] = None
    price: Optional[Decimal] = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v


class StockUpdateSchema(BaseModel):
    """Para ajuste manual de stock (PATCH /parts/{id}/stock)."""
    quantity: int   # nueva cantidad absoluta
    reason: str

    @field_validator("quantity")
    @classmethod
    def quantity_not_negative(cls, v):
        if v < 0:
            raise ValueError("El stock no puede ser negativo")
        return v


class PartOut(BaseModel):
    id: UUID
    sku: str
    name: str
    description: Optional[str]
    brand_id: Optional[UUID]
    brand: Optional[str]        # viene del @property en el modelo ORM
    category_id: Optional[UUID]
    category: Optional[str]     # viene del @property en el modelo ORM
    price: Decimal
    stock_quantity: int
    is_active: bool
    image_url: Optional[str] = None

    model_config = {"from_attributes": True}
