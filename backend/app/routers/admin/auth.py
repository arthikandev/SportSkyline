"""
SportSkyline Backend — Admin Router: Auth
POST /api/v1/admin/auth/*
"""
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_admin
from app.models.admin import Admin
from app.schemas.admin import AdminOut, LoginRequest, TokenResponse, RefreshRequest
from app.services.auth_service import login, refresh

router = APIRouter(prefix="/admin/auth", tags=["Admin – Auth"])


@router.post("/login", response_model=TokenResponse)
async def admin_login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate admin and return JWT tokens."""
    return await login(db, payload)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """Refresh access token using refresh token."""
    return await refresh(db, payload.refresh_token)


@router.get("/me", response_model=AdminOut)
async def me(admin: Admin = Depends(get_current_admin)):
    """Get currently authenticated admin profile."""
    return admin


@router.post("/logout")
async def logout():
    """
    Client-side logout — instruct client to discard tokens.
    For stateless JWT, no server action needed.
    """
    return {"message": "Logged out successfully. Please discard your tokens."}
