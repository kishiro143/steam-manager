from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from src.core.database import get_db
from src.core.deps import get_current_user, require_admin
from src.models.game import Genre
from src.models.user import User
from src.repositories.game_repository import SQLGameRepository
from src.schemas.schemas import GameCreate, GameUpdate, GameResponse

router = APIRouter(prefix="/api/v1/games", tags=["games"])


@router.get("", response_model=list[GameResponse])
def list_games(
    genre: Optional[Genre] = Query(default=None),
    price_max: Optional[float] = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, le=100),
    db: Session = Depends(get_db),
):
    return SQLGameRepository(db).get_all(genre=genre, price_max=price_max, skip=skip, limit=limit)


@router.get("/{game_id}", response_model=GameResponse)
def get_game(game_id: int, db: Session = Depends(get_db)):
    return SQLGameRepository(db).get_by_id(game_id)


@router.post("", response_model=GameResponse, status_code=201)
def create_game(
    data: GameCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return SQLGameRepository(db).create(data)


@router.put("/{game_id}", response_model=GameResponse)
def update_game(
    game_id: int,
    data: GameUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    return SQLGameRepository(db).update(game_id, data)


@router.delete("/{game_id}", status_code=204)
def delete_game(
    game_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    SQLGameRepository(db).delete(game_id)
