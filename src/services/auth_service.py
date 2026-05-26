from sqlalchemy.orm import Session
from src.models.user import User, UserRole
from src.schemas.schemas import RegisterRequest, LoginRequest, TokenResponse
from src.core.security import hash_password, verify_password, create_token
from src.core.exceptions import ConflictError, UnauthorizedError


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register(self, data: RegisterRequest) -> User:
        if self.db.query(User).filter(User.email == data.email).first():
            raise ConflictError("El email ya está registrado")
        if self.db.query(User).filter(User.username == data.username).first():
            raise ConflictError("El username ya está en uso")

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
            role=UserRole.user,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.db.query(User).filter(User.email == data.email).first()
        if not user or not verify_password(data.password, user.hashed_password):
            raise UnauthorizedError("Email o contraseña incorrectos")

        token = create_token(user.id, user.role.value)
        return TokenResponse(access_token=token, user_id=user.id, role=user.role.value)
