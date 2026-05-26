from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.core.database import get_db
from src.core.deps import get_current_user
from src.models.user import User
from src.services.library_review_service import LibraryService, ReviewService
from src.schemas.schemas import LibraryResponse, ReviewCreate, ReviewResponse

library_router = APIRouter(prefix="/api/v1/library", tags=["library"])
reviews_router = APIRouter(prefix="/api/v1/games", tags=["reviews"])


@library_router.get("", response_model=list[LibraryResponse])
def my_library(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return LibraryService(db).get_user_library(current_user.id)


@library_router.post("/{game_id}", response_model=LibraryResponse, status_code=201)
def add_to_library(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return LibraryService(db).add_game(current_user.id, game_id)


@library_router.delete("/{game_id}", status_code=204)
def remove_from_library(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    LibraryService(db).remove_game(current_user.id, game_id)


@reviews_router.get("/{game_id}/reviews", response_model=list[ReviewResponse])
def get_reviews(game_id: int, db: Session = Depends(get_db)):
    return ReviewService(db).get_reviews(game_id)


@reviews_router.post("/{game_id}/reviews", response_model=ReviewResponse, status_code=201)
def create_review(
    game_id: int,
    data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return ReviewService(db).create_review(current_user.id, game_id, data.rating, data.content)


@reviews_router.delete("/{game_id}/reviews/{review_id}", status_code=204)
def delete_review(
    game_id: int,
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ReviewService(db).delete_review(
        current_user.id, review_id,
        is_admin=(current_user.role.value == "admin")
    )
