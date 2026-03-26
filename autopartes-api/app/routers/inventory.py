from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional
from app.core.dependencies import get_db, require_staff
from app.models.inventory_log import InventoryLog, InventoryAction
from app.schemas.inventory_log import InventoryLogOut

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/logs", response_model=list[InventoryLogOut])
def list_logs(
    part_id: Optional[str] = None,
    action_type: Optional[InventoryAction] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _staff=Depends(require_staff),
):
    """Historial de movimientos de inventario. Solo staff y admin.

    Filtros opcionales:
    - part_id: UUID de la autoparte
    - action_type: restock | sale | adjustment | return
    """
    query = db.query(InventoryLog)

    if part_id:
        query = query.filter(InventoryLog.part_id == part_id)
    if action_type:
        query = query.filter(InventoryLog.action_type == action_type)

    return query.order_by(InventoryLog.created_at.desc()).offset(skip).limit(limit).all()
