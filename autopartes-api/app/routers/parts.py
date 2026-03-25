from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.dependencies import get_db, get_current_user, require_staff
from app.models.part import Part
from app.schemas.part import PartCreateSchema, PartUpdateSchema, PartOut

router = APIRouter(prefix="/parts", tags=["parts"])


@router.post("/", response_model=PartOut, status_code=201)
def create_part(
    payload: PartCreateSchema,
    db: Session = Depends(get_db),
    staff=Depends(require_staff)
):
    existing = db.query(Part).filter(Part.sku == payload.sku).first()
    if existing:
        raise HTTPException(status_code=400, detail="El SKU ya existe")

    part = Part(**payload.model_dump())
    db.add(part)
    db.commit()
    db.refresh(part)
    return part


@router.get("/", response_model=list[PartOut])
def list_parts(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    query = db.query(Part).filter(Part.is_active == True)

    if category:
        query = query.filter(Part.category == category)
    if brand:
        query = query.filter(Part.brand == brand)

    return query.offset(skip).limit(limit).all()


@router.get("/{part_id}", response_model=PartOut)
def get_part(
    part_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
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
    staff=Depends(require_staff)
):
    part = db.query(Part).filter(Part.id == part_id, Part.is_active == True).first()
    if not part:
        raise HTTPException(status_code=404, detail="Autoparte no encontrada")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(part, field, value)

    db.commit()
    db.refresh(part)
    return part


@router.delete("/{part_id}", status_code=204)
def delete_part(
    part_id: str,
    db: Session = Depends(get_db),
    staff=Depends(require_staff)
):
    part = db.query(Part).filter(Part.id == part_id, Part.is_active == True).first()
    if not part:
        raise HTTPException(status_code=404, detail="Autoparte no encontrada")

    part.is_active = False
    db.commit()