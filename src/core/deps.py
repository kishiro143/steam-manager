from fastapi import Depends, Header
from sqlalchemy.orm import Session
from typing import Optional
from src.core.database import get_db
from src.core.security import decode_token
from src.core.exceptions import UnauthorizedError, ForbiddenError
from src.models.user import User, UserRole


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError("Token requerido")
    token = authorization.split(" ")[1]
    payload = decode_token(token)
    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise UnauthorizedError("Usuario no encontrado")
    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != UserRole.admin:
        raise ForbiddenError("Se requiere rol admin")
    return current_user
