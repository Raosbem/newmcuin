from pydantic import BaseModel, field_validator
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from app.models.order import OrderStatus


class OrderItemCreateSchema(BaseModel):
    part_id: UUID
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_positive(cls, v):
        if v <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        return v


class OrderCreateSchema(BaseModel):
    items: List[OrderItemCreateSchema]

    @field_validator("items")
    @classmethod
    def items_not_empty(cls, v):
        if not v:
            raise ValueError("El pedido debe tener al menos un item")
        return v


class OrderItemOut(BaseModel):
    id: UUID
    part_id: UUID
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    model_config = {"from_attributes": True}


class OrderOut(BaseModel):
    id: UUID
    user_id: UUID
    status: OrderStatus
    total_amount: Decimal
    items: List[OrderItemOut]

    model_config = {"from_attributes": True}


class OrderStatusUpdateSchema(BaseModel):
    status: OrderStatus