from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user, require_staff
from app.models.brand import Brand
from app.models.part import Part
from app.schemas.brand import BrandCreateSchema, BrandUpdateSchema, BrandOut

router = APIRouter(prefix="/brands", tags=["brands"])


@router.get("/", response_model=list[BrandOut])
def list_brands(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return db.query(Brand).order_by(Brand.name).all()


@router.post("/", response_model=BrandOut, status_code=201)
def create_brand(
    payload: BrandCreateSchema,
    db: Session = Depends(get_db),
    _=Depends(require_staff),
):
    if db.query(Brand).filter(Brand.name == payload.name).first():
        raise HTTPException(status_code=400, detail="La marca ya existe")
    brand = Brand(name=payload.name)
    db.add(brand)
    db.commit()
    db.refresh(brand)
    return brand


@router.get("/{brand_id}", response_model=BrandOut)
def get_brand(
    brand_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    return brand


@router.put("/{brand_id}", response_model=BrandOut)
def update_brand(
    brand_id: str,
    payload: BrandUpdateSchema,
    db: Session = Depends(get_db),
    _=Depends(require_staff),
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    if db.query(Brand).filter(Brand.name == payload.name, Brand.id != brand_id).first():
        raise HTTPException(status_code=400, detail="Ya existe una marca con ese nombre")
    brand.name = payload.name
    db.commit()
    db.refresh(brand)
    return brand


@router.delete("/{brand_id}", status_code=204)
def delete_brand(
    brand_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_staff),
):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    if not brand:
        raise HTTPException(status_code=404, detail="Marca no encontrada")
    active_parts = db.query(Part).filter(Part.brand_id == brand_id, Part.is_active == True).count()
    if active_parts > 0:
        raise HTTPException(status_code=400, detail=f"No se puede eliminar: {active_parts} autoparte(s) la usan")
    db.delete(brand)
    db.commit()
