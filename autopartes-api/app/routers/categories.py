from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user, require_staff
from app.models.category import Category
from app.models.part import Part
from app.schemas.category import CategoryCreateSchema, CategoryUpdateSchema, CategoryOut

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=list[CategoryOut])
def list_categories(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    return db.query(Category).order_by(Category.name).all()


@router.post("/", response_model=CategoryOut, status_code=201)
def create_category(
    payload: CategoryCreateSchema,
    db: Session = Depends(get_db),
    _=Depends(require_staff),
):
    if db.query(Category).filter(Category.name == payload.name).first():
        raise HTTPException(status_code=400, detail="La categoría ya existe")
    category = Category(name=payload.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("/{category_id}", response_model=CategoryOut)
def get_category(
    category_id: str,
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return category


@router.put("/{category_id}", response_model=CategoryOut)
def update_category(
    category_id: str,
    payload: CategoryUpdateSchema,
    db: Session = Depends(get_db),
    _=Depends(require_staff),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    if db.query(Category).filter(Category.name == payload.name, Category.id != category_id).first():
        raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")
    category.name = payload.name
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: str,
    db: Session = Depends(get_db),
    _=Depends(require_staff),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    active_parts = db.query(Part).filter(Part.category_id == category_id, Part.is_active == True).count()
    if active_parts > 0:
        raise HTTPException(status_code=400, detail=f"No se puede eliminar: {active_parts} autoparte(s) la usan")
    db.delete(category)
    db.commit()
