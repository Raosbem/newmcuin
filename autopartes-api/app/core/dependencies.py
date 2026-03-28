from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.core.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(status_code=401, detail="Token inválido o expirado")

    from app.models.user import User
    user = db.query(User).filter(User.id == payload["sub"]).first()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuario no encontrado o inactivo")

    return user


def require_staff(user=Depends(get_current_user)):
    if user.role not in ("staff", "admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Acceso solo para personal interno")
    return user


def require_admin(user=Depends(get_current_user)):
    if user.role not in ("admin", "superadmin"):
        raise HTTPException(status_code=403, detail="Acceso solo para administradores")
    return user


def require_superadmin(user=Depends(get_current_user)):
    if user.role != "superadmin":
        raise HTTPException(status_code=403, detail="Acceso solo para superadmin")
    return user