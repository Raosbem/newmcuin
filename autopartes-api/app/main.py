from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.exceptions import value_error_handler, permission_error_handler
from app.db.session import engine
from app.models.base import Base
from app.models import user, part, order, inventory_log  # registra todos los modelos en Base
from app.routers import auth, users, parts, orders, reports, inventory

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 App iniciando SIN BD")
    yield


app = FastAPI(
    title="Autopartes API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(ValueError, value_error_handler)
app.add_exception_handler(PermissionError, permission_error_handler)

app.include_router(auth.router,    prefix="/api/v1")
app.include_router(users.router,   prefix="/api/v1")
app.include_router(parts.router,   prefix="/api/v1")
app.include_router(orders.router,  prefix="/api/v1")
app.include_router(reports.router,    prefix="/api/v1")
app.include_router(inventory.router,  prefix="/api/v1")

@app.get("/")
def root():
    return {"status": "ok", "docs": "/docs"}
