"""SportSkyline Backend — Public Routers Package"""
from fastapi import APIRouter
from app.routers.public.homepage import router as homepage_router
from app.routers.public.articles import router as articles_router
from app.routers.public.matches import router as matches_router
from app.routers.public.search import router as search_router
from app.routers.public.ads import router as ads_router

public_router = APIRouter(prefix="/api/v1")
public_router.include_router(homepage_router)
public_router.include_router(articles_router)
public_router.include_router(matches_router)
public_router.include_router(search_router)
public_router.include_router(ads_router)
