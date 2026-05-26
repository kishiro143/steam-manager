from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from src.core.database import Base


class Library(Base):
    __tablename__ = "library"
    __table_args__ = (UniqueConstraint("user_id", "game_id", name="uq_user_game"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False)
    added_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    total_minutes = Column(Integer, default=0)

    user = relationship("User", back_populates="library")
    game = relationship("Game", back_populates="library_entries")
