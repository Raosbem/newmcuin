from sqlalchemy.orm import Session
from app.models.part import Part


class PartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, part_id) -> Part | None:
        return self.db.get(Part, str(part_id))

    def decrement_stock(self, part_id, quantity: int):
        part = self.get_by_id(part_id)
        if part:
            part.stock_quantity -= quantity
