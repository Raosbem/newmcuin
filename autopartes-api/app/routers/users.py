from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.core.security import hash_password
from app.schemas.user import UserRegisterSchema, UserOut
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserOut, status_code=201)
def register(payload: UserRegisterSchema, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

    user = User(
        email           = payload.email,
        hashed_password = hash_password(payload.password),
        full_name       = payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user