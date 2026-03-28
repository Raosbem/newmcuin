import os
import random
import shutil
import string
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.core.dependencies import get_db, get_current_user, require_staff
from app.models.inventory_log import InventoryLog, InventoryAction
from app.models.part import Part
from app.schemas.part import PartCreateSchema, PartUpdateSchema, PartOut, StockUpdateSchema

router = APIRouter(prefix="/parts", tags=["parts"])


def _generate_sku(db: Session) -> str:
    """Genera un SKU único con formato SKU-YYYYMMDD-XXXX."""
    date_str = datetime.now().strftime("%Y%m%d")
    for _ in range(10):
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        sku = f"SKU-{date_str}-{suffix}"
        if not db.query(Part).filter(Part.sku == sku).first():
            return sku
    raise HTTPException(status_code=500, detail="No se pudo generar un SKU único")


@router.post("/", response_model=PartOut, status_code=201)
def create_part(
    payload: PartCreateSchema,
    db: Session = Depends(get_db),
    staff=Depends(require_staff),
):
    sku = _generate_sku(db)
    part = Part(sku=sku, **payload.model_dump())
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


@router.get("/", response_model=list[PartOut])
def list_parts(
    search: Optional[str] = None,
    brand_id: Optional[UUID] = None,
    category_id: Optional[UUID] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Part).filter(Part.is_active == True)
    if search:
        query = query.filter(Part.name.ilike(f"%{search}%"))
    if brand_id:
        query = query.filter(Part.brand_id == brand_id)
    if category_id:
        query = query.filter(Part.category_id == category_id)
    return query.offset(skip).limit(limit).all()


@router.get("/{part_id}", response_model=PartOut)
def get_part(
    part_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    part = db.query(Part).filter(Part.id == part_id, Part.is_active == True).first()
    if not part:
        raise HTTPException(status_code=404, detail="Autoparte no encontrada")
    return part


@router.put("/{part_id}", response_model=PartOut)
def update_part(
    part_id: str,
    payload: PartUpdateSchema,
    db: Session = Depends(get_db),
    staff=Depends(require_staff),
):
    part = db.query(Part).filter(Part.id == part_id, Part.is_active == True).first()
    if not part:
        raise HTTPException(status_code=404, detail="Autoparte no encontrada")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(part, field, value)

    db.commit()
    db.refresh(part)
    return part


@router.patch("/{part_id}/stock", response_model=PartOut)
def update_stock(
    part_id: str,
    payload: StockUpdateSchema,
    db: Session = Depends(get_db),
    staff=Depends(require_staff),
):
    """Ajuste manual de stock. Registra un InventoryLog con action_type='adjustment'."""
    part = db.query(Part).filter(Part.id == part_id, Part.is_active == True).first()
    if not part:
        raise HTTPException(status_code=404, detail="Autoparte no encontrada")

    qty_before = part.stock_quantity
    part.stock_quantity = payload.quantity

    log = InventoryLog(
        part_id         = part.id,
        user_id         = staff.id,
        action_type     = InventoryAction.ADJUSTMENT,
        quantity_before = qty_before,
        quantity_after  = payload.quantity,
        delta           = payload.quantity - qty_before,
        reason          = payload.reason,
    )
    db.add(log)
    db.commit()
    db.refresh(part)
    return part


@router.delete("/{part_id}", status_code=204)
def delete_part(
    part_id: str,
    db: Session = Depends(get_db),
    staff=Depends(require_staff),
):
    part = db.query(Part).filter(Part.id == part_id, Part.is_active == True).first()
    if not part:
        raise HTTPException(status_code=404, detail="Autoparte no encontrada")

    part.is_active = False
    db.commit()


@router.post("/{part_id}/image", response_model=PartOut)
def upload_image(
    part_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    staff=Depends(require_staff),
):
    part = db.query(Part).filter(Part.id == part_id, Part.is_active == True).first()
    if not part:
        raise HTTPException(status_code=404, detail="Autoparte no encontrada")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in (file.filename or "") else "jpg"
    if ext not in ("jpg", "jpeg", "png", "webp"):
        raise HTTPException(status_code=400, detail="Formato no permitido. Use JPG, PNG o WebP")

    os.makedirs("/app/static/images", exist_ok=True)
    filename = f"{part_id}.{ext}"
    with open(f"/app/static/images/{filename}", "wb") as f:
        shutil.copyfileobj(file.file, f)

    part.image_url = f"/static/images/{filename}"
    db.commit()
    db.refresh(part)
    return part
