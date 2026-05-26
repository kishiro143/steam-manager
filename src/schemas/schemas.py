from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from src.models.user import UserRole
from src.models.game import GameType, Genre


# ── Auth ───────────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    username: str
    password: str

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

    @field_validator("username")
    @classmethod
    def username_length(cls, v: str) -> str:
        if len(v) < 3:
            raise ValueError("El username debe tener al menos 3 caracteres")
        return v.lower().strip()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str


# ── User ───────────────────────────────────────────────────────────────────────
class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: UserRole
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Game ───────────────────────────────────────────────────────────────────────
class GameCreate(BaseModel):
    title: str
    description: Optional[str] = None
    genre: Genre
    game_type: GameType
    price: float = 0.0
    cover_url: Optional[str] = None
    game_url: Optional[str] = None
    developer: Optional[str] = None

    @field_validator("price")
    @classmethod
    def price_non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("El precio no puede ser negativo")
        return round(v, 2)


class GameUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    cover_url: Optional[str] = None
    game_url: Optional[str] = None
    developer: Optional[str] = None


class GameResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    genre: Genre
    game_type: GameType
    price: float
    cover_url: Optional[str]
    game_url: Optional[str]
    developer: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Library ────────────────────────────────────────────────────────────────────
class LibraryResponse(BaseModel):
    id: int
    game_id: int
    added_at: datetime
    total_minutes: int
    game: GameResponse

    model_config = {"from_attributes": True}


# ── Review ─────────────────────────────────────────────────────────────────────
class ReviewCreate(BaseModel):
    rating: int
    content: Optional[str] = None

    @field_validator("rating")
    @classmethod
    def rating_range(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("El rating debe estar entre 1 y 5")
        return v


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    game_id: int
    rating: int
    content: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}
