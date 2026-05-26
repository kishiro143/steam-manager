from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from src.core.database import Base, engine, SessionLocal
from src.core.exceptions import AppException, app_exception_handler, generic_exception_handler
from src.core.config import get_settings
from src.routers.auth_router import router as auth_router
from src.routers.games_router import router as games_router
from src.routers.library_reviews_router import library_router, reviews_router
from src.routers.users_router import router as users_router

settings = get_settings()


def seed_initial_data():
    from src.models.user import User, UserRole
    from src.models.game import Game, GameFactory, GameType, Genre
    from src.core.security import hash_password
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                email=settings.ADMIN_EMAIL,
                username="admin",
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                role=UserRole.admin,
            )
            db.add(admin)
        if db.query(Game).count() == 0:
            seeds = [
                GameFactory.create(GameType.indie, title="Culebrita", genre=Genre.action, description="Clasico juego de la serpiente. Come manzanas y crece sin chocarte.", price=0.0, developer="Proyecto Steam", game_url="/static/games/01-culebrita.html"),
                GameFactory.create(GameType.indie, title="Tres en Raya", genre=Genre.strategy, description="El clasico juego de X y O para dos jugadores.", price=0.0, developer="Proyecto Steam", game_url="/static/games/02-tres-en-raya.html"),
                GameFactory.create(GameType.indie, title="Ajedrez Mini", genre=Genre.strategy, description="Ajedrez completo en tu navegador. Piezas funcionales y movimientos reales.", price=0.0, developer="Proyecto Steam", game_url="/static/games/03-ajedrez-mini.html"),
                GameFactory.create(GameType.indie, title="Piedra Papel Tijera", genre=Genre.action, description="El clasico juego de manos contra la maquina. Tres rondas para ganar.", price=0.0, developer="Proyecto Steam", game_url="/static/games/05-piedra-papel-tijera.html"),
                GameFactory.create(GameType.indie, title="Buscaminas Lite", genre=Genre.puzzle, description="Buscaminas clasico con tablero 9x9 y 10 minas. Cuidado con las explosiones.", price=0.0, developer="Proyecto Steam", game_url="/static/games/07-buscaminas-lite.html"),
                GameFactory.create(GameType.indie, title="Rompecabezas 8", genre=Genre.puzzle, description="Rompecabezas deslizante de 8 piezas. Ordena los numeros del 1 al 8.", price=0.0, developer="Proyecto Steam", game_url="/static/games/12-rompecabezas-8.html"),
            ]
            db.add_all(seeds)
        db.commit()
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    seed_initial_data()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Gestor de videojuegos tipo Steam — FastAPI + MVC + SOLID",
    lifespan=lifespan,
)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

app.include_router(auth_router)
app.include_router(games_router)
app.include_router(library_router)
app.include_router(reviews_router)
app.include_router(users_router)

app.mount("/static", StaticFiles(directory="src/static"), name="static")


@app.get("/api/v1/health")
def health():
    return {"status": "ok", "version": settings.APP_VERSION, "env": settings.APP_ENV}


@app.get("/", include_in_schema=False)
def root():
    return FileResponse("src/static/index.html")
