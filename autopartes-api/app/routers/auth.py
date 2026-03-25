from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.core.security import verify_password, create_access_token
from app.schemas.auth import LoginSchema, TokenOut
from app.schemas.user import UserOut
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenOut)
def login(payload: LoginSchema, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuario inactivo")

    token = create_access_token(subject=str(user.id), role=user.role)
    return TokenOut(access_token=token)


@router.get("/me", response_model=UserOut)
def me(current_user=Depends(get_current_user)):
    return current_user