from fastapi import FastAPI

from src.infrastructure.config.settings import settings
from src.interfaces.api.exception_handlers import auth_exception_handler
from src.interfaces.api.routes.auth import router as auth_router
from src.interfaces.api.routes.meal_plan import router as meal_plan_router

app = FastAPI(title=settings.app.title)

auth_exception_handler(app)

all_routers = [auth_router, meal_plan_router]
for r in all_routers:
    app.include_router(r)
