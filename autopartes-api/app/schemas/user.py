from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.models.user import UserRole


class UserRegisterSchema(BaseModel):
    """Registro público de clientes externos (siempre crea role=customer)."""
    email: str
    password: str
    full_name: str


class UserCreateInternalSchema(BaseModel):
    """Solo admin: crea usuarios internos (staff o admin)."""
    email: str
    password: str
    full_name: str
    role: UserRole


class UserUpdateSchema(BaseModel):
    """Solo admin: actualiza datos de cualquier usuario."""
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
