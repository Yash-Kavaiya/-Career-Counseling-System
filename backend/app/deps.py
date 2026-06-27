"""Shared FastAPI dependencies: DB session and current-user (JWT)."""
from __future__ import annotations

from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models.user import User
from .security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        user_id = int(payload.get("sub"))
    except Exception:  # noqa: BLE001 - any decode/cast failure is an auth failure
        raise credentials_exc
    user = db.get(User, user_id)
    if user is None:
        raise credentials_exc
    return user
