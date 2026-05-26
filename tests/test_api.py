import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.database import Base, get_db
from main import app

# DB en memoria para tests
TEST_DB = "sqlite:///./test.db"
engine = create_engine(TEST_DB, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app, raise_server_exceptions=False)


def test_health():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_and_login():
    r = client.post("/api/v1/auth/register", json={
        "email": "test@test.com", "username": "testuser", "password": "Test1234!"
    })
    assert r.status_code == 201
    assert r.json()["email"] == "test@test.com"

    r = client.post("/api/v1/auth/login", json={
        "email": "test@test.com", "password": "Test1234!"
    })
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_register_duplicate_email():
    for _ in range(2):
        r = client.post("/api/v1/auth/register", json={
            "email": "dup@test.com", "username": f"user{_}", "password": "Test1234!"
        })
    assert r.status_code == 409


def test_login_wrong_password():
    client.post("/api/v1/auth/register", json={
        "email": "x@test.com", "username": "xuser", "password": "Test1234!"
    })
    r = client.post("/api/v1/auth/login", json={"email": "x@test.com", "password": "Wrong!"})
    assert r.status_code == 401


def test_get_games_public():
    r = client.get("/api/v1/games")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_create_game_requires_admin():
    r = client.post("/api/v1/games", json={
        "title": "Test Game", "genre": "action", "game_type": "indie", "price": 9.99
    })
    assert r.status_code == 401


def get_admin_token():
    from src.core.database import SessionLocal
    from src.models.user import User, UserRole
    from src.core.security import hash_password, create_token
    db = SessionLocal()
    admin = User(email="a@a.com", username="admin2", hashed_password=hash_password("Admin1!"), role=UserRole.admin)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    token = create_token(admin.id, "admin")
    db.close()
    return token


def test_create_game_as_admin():
    token = get_admin_token()
    r = client.post("/api/v1/games",
        json={"title": "New Game", "genre": "rpg", "game_type": "indie", "price": 14.99},
        headers={"Authorization": f"Bearer {token}"}
    )
    assert r.status_code == 201
    assert r.json()["title"] == "New Game"
