from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.inventory_log import InventoryAction


class InventoryLogOut(BaseModel):
    id: UUID
    part_id: UUID
    user_id: UUID
    action_type: InventoryAction
    quantity_before: int
    quantity_after: int
    delta: int
    reason: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
