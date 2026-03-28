from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app.core.dependencies import get_db, require_admin
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.schemas.user import (
    UserRegisterSchema,
    UserCreateInternalSchema,
    UserUpdateSchema,
    UserOut,
)

# Roles que solo el superadmin puede asignar o gestionar
_ADMIN_ROLES = {UserRole.ADMIN, UserRole.SUPERADMIN}

router = APIRouter(prefix="/users", tags=["users"])


# ──────────────────────────────────────────────
# Público: registro de clientes externos
# ──────────────────────────────────────────────

@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserRegisterSchema, db: Session = Depends(get_db)):
    """Registro abierto. Siempre crea un usuario con role=customer."""
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    user = User(
        email           = payload.email,
        hashed_password = hash_password(payload.password),
        full_name       = payload.full_name,
        role            = UserRole.CUSTOMER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ──────────────────────────────────────────────
# Solo admin: gestión de usuarios internos
# ──────────────────────────────────────────────

@router.get("/", response_model=list[UserOut])
def list_users(
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Lista todos los usuarios. Filtros opcionales: role, is_active."""
    query = db.query(User)
    if role is not None:
        query = query.filter(User.role == role)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    return query.order_by(User.full_name).offset(skip).limit(limit).all()


@router.get("/{user_id}", response_model=UserOut)
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    """Detalle de un usuario por ID."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.post("/", response_model=UserOut, status_code=201)
def create_internal_user(
    payload: UserCreateInternalSchema,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    """Crea un usuario interno. Solo superadmin puede crear roles admin/superadmin."""
    if payload.role in _ADMIN_ROLES and current_admin.role != "superadmin":
        raise HTTPException(
            status_code=403,
            detail="Solo el superadmin puede crear administradores",
        )
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    user = User(
        email           = payload.email,
        hashed_password = hash_password(payload.password),
        full_name       = payload.full_name,
        role            = payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(
    user_id: str,
    payload: UserUpdateSchema,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    """Actualiza nombre, rol o estado activo de un usuario. Solo admin/superadmin."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Solo superadmin puede modificar usuarios con rol admin/superadmin
    if user.role in _ADMIN_ROLES and current_admin.role != "superadmin":
        raise HTTPException(
            status_code=403,
            detail="Solo el superadmin puede modificar administradores",
        )
    # Solo superadmin puede asignar rol admin/superadmin
    new_role = payload.model_dump(exclude_unset=True).get("role")
    if new_role and UserRole(new_role) in _ADMIN_ROLES and current_admin.role != "superadmin":
        raise HTTPException(
            status_code=403,
            detail="Solo el superadmin puede asignar rol de administrador",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}/toggle-active", response_model=UserOut)
def toggle_active(
    user_id: str,
    db: Session = Depends(get_db),
    current_admin=Depends(require_admin),
):
    """Activa o desactiva un usuario. Admins no pueden tocar a otros admins."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if user.role in _ADMIN_ROLES and current_admin.role != "superadmin":
        raise HTTPException(
            status_code=403,
            detail="Solo el superadmin puede activar/desactivar administradores",
        )

    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user
