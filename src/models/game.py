from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from src.core.database import Base


class GameType(str, enum.Enum):
    indie = "indie"
    aaa = "aaa"
    free_to_play = "free_to_play"
    early_access = "early_access"


class Genre(str, enum.Enum):
    action = "action"
    adventure = "adventure"
    rpg = "rpg"
    strategy = "strategy"
    puzzle = "puzzle"
    platformer = "platformer"
    simulation = "simulation"
    horror = "horror"


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    genre = Column(SAEnum(Genre), nullable=False)
    game_type = Column(SAEnum(GameType), nullable=False)
    price = Column(Float, default=0.0)
    cover_url = Column(String, nullable=True)
    game_url = Column(String, nullable=True)
    developer = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    library_entries = relationship("Library", back_populates="game", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="game", cascade="all, delete-orphan")


# ── Factory Method ─────────────────────────────────────────────────────────────
class GameFactory:
    """Crea instancias de Game con defaults según el tipo. (Patrón Factory Method)"""

    @staticmethod
    def create(game_type: GameType, **kwargs) -> Game:
        defaults = {
            GameType.indie:        {"price": 9.99,  "developer": "Indie Dev"},
            GameType.aaa:          {"price": 59.99, "developer": "Major Studio"},
            GameType.free_to_play: {"price": 0.0,   "developer": "F2P Studio"},
            GameType.early_access: {"price": 19.99, "developer": "Early Dev"},
        }
        params = {**defaults.get(game_type, {}), **kwargs, "game_type": game_type}
        return Game(**params)
