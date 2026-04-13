"""
SportSkyline Backend — Auth Service
Handles login, token creation, password management.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.middleware.auth import (
    create_access_token, create_refresh_token,
    decode_token, hash_password, verify_password,
)
from app.models.admin import Admin
from app.schemas.admin import LoginRequest, TokenResponse


async def login(db: AsyncSession, payload: LoginRequest) -> TokenResponse:
    result = await db.execute(
        select(Admin).where(
            Admin.email == payload.email,
            Admin.deleted_at.is_(None),
        )
    )
    admin = result.scalar_one_or_none()

    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    # Update last login
    admin.last_login_at = datetime.now(timezone.utc)
    await db.flush()

    role_name = admin.role.name if admin.role else None
    access_token = create_access_token(admin.id, role=role_name)
    refresh_token = create_refresh_token(admin.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


async def refresh(db: AsyncSession, refresh_token: str) -> TokenResponse:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    admin_id = payload.get("sub")
    result = await db.execute(
        select(Admin).where(Admin.id == uuid.UUID(admin_id), Admin.is_active.is_(True))
    )
    admin = result.scalar_one_or_none()
    if not admin:
        raise HTTPException(status_code=401, detail="Admin not found")

    role_name = admin.role.name if admin.role else None
    new_access = create_access_token(admin.id, role=role_name)
    new_refresh = create_refresh_token(admin.id)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


async def create_first_admin(db: AsyncSession) -> None:
    """Bootstrap the first super_admin if none exist."""
    from app.models.admin import Role
    result = await db.execute(select(Admin).limit(1))
    if result.scalar_one_or_none():
        return  # Admins exist, skip

    # Ensure super_admin role exists
    role_result = await db.execute(select(Role).where(Role.name == "super_admin"))
    role = role_result.scalar_one_or_none()
    if not role:
        role = Role(name="super_admin", description="Full access administrator")
        db.add(role)
        await db.flush()
        await db.refresh(role)

    # Create editor role
    ed_result = await db.execute(select(Role).where(Role.name == "editor"))
    if not ed_result.scalar_one_or_none():
        db.add(Role(name="editor", description="Can create and edit articles"))

    # Create moderator role
    mod_result = await db.execute(select(Role).where(Role.name == "moderator"))
    if not mod_result.scalar_one_or_none():
        db.add(Role(name="moderator", description="Can review and moderate content"))

    admin = Admin(
        email=settings.first_admin_email,
        password_hash=hash_password(settings.first_admin_password),
        full_name=settings.first_admin_name,
        role_id=role.id,
    )
    db.add(admin)
    await db.flush()
