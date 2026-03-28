from pydantic import BaseModel
from uuid import UUID


class BrandCreateSchema(BaseModel):
    name: str


class BrandUpdateSchema(BaseModel):
    name: str


class BrandOut(BaseModel):
    id: UUID
    name: str

    model_config = {"from_attributes": True}
