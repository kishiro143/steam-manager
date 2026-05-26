from sqlalchemy.orm import Session
from src.models.library import Library
from src.models.review import Review
from src.repositories.game_repository import SQLGameRepository
from src.core.exceptions import ConflictError, NotFoundError, ForbiddenError


class LibraryService:
    def __init__(self, db: Session):
        self.db = db
        self.game_repo = SQLGameRepository(db)

    def get_user_library(self, user_id: int) -> list[Library]:
        return self.db.query(Library).filter(Library.user_id == user_id).all()

    def add_game(self, user_id: int, game_id: int) -> Library:
        self.game_repo.get_by_id(game_id)  # lanza NotFoundError si no existe
        existing = self.db.query(Library).filter(
            Library.user_id == user_id, Library.game_id == game_id
        ).first()
        if existing:
            raise ConflictError("El juego ya está en tu biblioteca")
        entry = Library(user_id=user_id, game_id=game_id)
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    def remove_game(self, user_id: int, game_id: int) -> None:
        entry = self.db.query(Library).filter(
            Library.user_id == user_id, Library.game_id == game_id
        ).first()
        if not entry:
            raise NotFoundError("Juego en biblioteca")
        self.db.delete(entry)
        self.db.commit()


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.game_repo = SQLGameRepository(db)

    def get_reviews(self, game_id: int) -> list[Review]:
        self.game_repo.get_by_id(game_id)
        return self.db.query(Review).filter(Review.game_id == game_id).all()

    def create_review(self, user_id: int, game_id: int, rating: int, content: str | None) -> Review:
        self.game_repo.get_by_id(game_id)
        if self.db.query(Review).filter(Review.user_id == user_id, Review.game_id == game_id).first():
            raise ConflictError("Ya escribiste una reseña para este juego")
        review = Review(user_id=user_id, game_id=game_id, rating=rating, content=content)
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def delete_review(self, user_id: int, review_id: int, is_admin: bool) -> None:
        review = self.db.query(Review).filter(Review.id == review_id).first()
        if not review:
            raise NotFoundError("Reseña")
        if not is_admin and review.user_id != user_id:
            raise ForbiddenError("No puedes borrar la reseña de otro usuario")
        self.db.delete(review)
        self.db.commit()
