"""
Application entry point.
FastAPI app, CORS, global error handling, lifespan (DB init).
"""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.router import api_router
from app.core.config import get_settings
from app.core.database import Base, engine

settings = get_settings()
logger = logging.getLogger("apk_manager")

# Resolve directories relative to this file so they work regardless of cwd
BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Wait for DB (handled by Alembic in prod)."""
    # Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified/created by Alembic.")
    yield
    logger.info("Application shutting down.")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Global Error Handler ─────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "data": None, "error": "Internal server error"},
    )


# ─── API Routes ───────────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api")

# ─── Static Files & Templates ─────────────────────────────────────────────────
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", include_in_schema=False)
async def serve_root(request: Request):
    """Serve the SPA shell."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/{path:path}", include_in_schema=False)
async def serve_spa(request: Request, path: str):
    """Catch-all: serve SPA for client-side navigation (skip /api routes)."""
    if path.startswith("api/"):
        return JSONResponse(status_code=404, content={"detail": "Not found"})
    return templates.TemplateResponse("index.html", {"request": request})

