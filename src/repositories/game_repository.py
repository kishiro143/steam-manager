from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.orm import Session
from src.models.game import Game, GameType, Genre, GameFactory
from src.schemas.schemas import GameCreate, GameUpdate
from src.core.exceptions import NotFoundError


# ── Interfaz (SOLID: D — depender de abstracciones) ───────────────────────────
class IGameRepository(ABC):
    @abstractmethod
    def get_all(self, genre: Optional[Genre], price_max: Optional[float], skip: int, limit: int) -> list[Game]: ...
    @abstractmethod
    def get_by_id(self, game_id: int) -> Game: ...
    @abstractmethod
    def create(self, data: GameCreate) -> Game: ...
    @abstractmethod
    def update(self, game_id: int, data: GameUpdate) -> Game: ...
    @abstractmethod
    def delete(self, game_id: int) -> None: ...


# ── Implementación PostgreSQL / SQLite ────────────────────────────────────────
class SQLGameRepository(IGameRepository):
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, genre=None, price_max=None, skip=0, limit=20) -> list[Game]:
        query = self.db.query(Game)
        if genre:
            query = query.filter(Game.genre == genre)
        if price_max is not None:
            query = query.filter(Game.price <= price_max)
        return query.offset(skip).limit(limit).all()

    def get_by_id(self, game_id: int) -> Game:
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game:
            raise NotFoundError("Juego")
        return game

    def create(self, data: GameCreate) -> Game:
        # Usa el Factory para crear con defaults según el tipo
        params = data.model_dump(); params.pop("game_type"); game = GameFactory.create(data.game_type, **params)
        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)
        return game

    def update(self, game_id: int, data: GameUpdate) -> Game:
        game = self.get_by_id(game_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(game, field, value)
        self.db.commit()
        self.db.refresh(game)
        return game

    def delete(self, game_id: int) -> None:
        game = self.get_by_id(game_id)
        self.db.delete(game)
        self.db.commit()
