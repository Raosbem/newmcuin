from pydantic import BaseModel
from uuid import UUID


class CategoryCreateSchema(BaseModel):
    name: str


class CategoryUpdateSchema(BaseModel):
    name: str


class CategoryOut(BaseModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}
