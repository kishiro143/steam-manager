from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from src.core.database import get_db
from src.core.deps import require_admin
from src.core.exceptions import NotFoundError, ForbiddenError
from src.models.user import User, UserRole
from src.models.library import Library
from src.models.game import Game

router = APIRouter(prefix="/api/v1/users", tags=["users"])


class UserAdminResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    created_at: datetime
    total_games: int
    total_minutes: int

    model_config = {"from_attributes": True}


class UserGameDetail(BaseModel):
    game_id: int
    game_title: str
    total_minutes: int
    added_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=list[UserAdminResponse])
def list_users(db: Session = Depends(get_db), _=Depends(require_admin)):
    users = db.query(User).order_by(User.id).all()
    result = []
    for u in users:
        lib = db.query(Library).filter(Library.user_id == u.id).all()
        total_minutes = sum(e.total_minutes or 0 for e in lib)
        result.append(UserAdminResponse(
            id=u.id,
            email=u.email,
            username=u.username,
            role=u.role.value,
            created_at=u.created_at,
            total_games=len(lib),
            total_minutes=total_minutes,
        ))
    return result


@router.get("/{user_id}/games", response_model=list[UserGameDetail])
def user_games(user_id: int, db: Session = Depends(get_db), _=Depends(require_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("Usuario")
    entries = db.query(Library, Game).join(Game, Library.game_id == Game.id)\
        .filter(Library.user_id == user_id).all()
    return [UserGameDetail(
        game_id=lib.game_id,
        game_title=game.title,
        total_minutes=lib.total_minutes or 0,
        added_at=lib.added_at,
    ) for lib, game in entries]


@router.put("/{user_id}/role", response_model=UserAdminResponse)
def change_role(user_id: int, db: Session = Depends(get_db), current_admin=Depends(require_admin)):
    if user_id == current_admin.id:
        raise ForbiddenError("No puedes cambiar tu propio rol")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("Usuario")
    user.role = UserRole.admin if user.role == UserRole.user else UserRole.user
    db.commit()
    db.refresh(user)
    lib = db.query(Library).filter(Library.user_id == user.id).all()
    return UserAdminResponse(
        id=user.id, email=user.email, username=user.username,
        role=user.role.value, created_at=user.created_at,
        total_games=len(lib), total_minutes=sum(e.total_minutes or 0 for e in lib),
    )


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin=Depends(require_admin)):
    if user_id == current_admin.id:
        raise ForbiddenError("No puedes eliminar tu propia cuenta")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise NotFoundError("Usuario")
    db.delete(user)
    db.commit()
