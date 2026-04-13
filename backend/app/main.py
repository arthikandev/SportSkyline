"""
SportSkyline Backend — Main Entry Point
FastAPI application initialization.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import engine
from app.routers.public import public_router
from app.routers.admin.auth import router as admin_auth_router
from app.routers.admin.articles import router as admin_articles_router
from app.routers.admin.categories import router as admin_categories_router
from app.routers.admin.sports import router as admin_sports_router
from app.routers.admin.teams import router as admin_teams_router
from app.routers.admin.matches import router as admin_matches_router
from app.routers.admin.ads import router as admin_ads_router
from app.services.auth_service import create_first_admin
from app.database import get_db_context


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("SportSkyline API starting up...")
    
    # Bootstrap admin
    async with get_db_context() as db:
        await create_first_admin(db)
    
    yield
    
    # Shutdown
    logger.info("SportSkyline API shutting down...")
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for SportSkyline - Sports News & Live Scores",
    lifespan=lifespan,
    debug=settings.debug,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Public API
app.include_router(public_router)

# Admin API
admin_prefix = "/api/v1"
app.include_router(admin_auth_router, prefix=admin_prefix)
app.include_router(admin_articles_router, prefix=admin_prefix)
app.include_router(admin_categories_router, prefix=admin_prefix)
app.include_router(admin_sports_router, prefix=admin_prefix)
app.include_router(admin_teams_router, prefix=admin_prefix)
app.include_router(admin_matches_router, prefix=admin_prefix)
app.include_router(admin_ads_router, prefix=admin_prefix)

# --- Serving Static Frontend ---
# Admin Dashboard at /admin
app.mount("/admin", StaticFiles(directory="admin_dashboard", html=True), name="admin")

# Static Assets (JS companion files)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Main Website at root (must be last)
app.mount("/", StaticFiles(directory="..", html=True), name="site")


@app.get("/health")
async def health_check():
    return {"status": "ok", "version": settings.app_version}
