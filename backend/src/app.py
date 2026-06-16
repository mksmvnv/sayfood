from fastapi import FastAPI

from src.infrastructure.config.settings import settings
from src.interfaces.api.exception_handlers import auth_exception_handler
from src.interfaces.api.routes.auth import router as auth_router

app = FastAPI(title=settings.app.title)

auth_exception_handler(app)

app.include_router(auth_router)
