from pydantic import BaseModel, EmailStr
from uuid import UUID
from app.models.user import UserRole


class UserRegisterSchema(BaseModel):
    email: str
    password: str
    full_name: str


class UserOut(BaseModel):
    id: UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}