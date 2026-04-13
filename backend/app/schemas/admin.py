"""
SportSkyline Backend — Pydantic v2 Schemas: Admin, Auth
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Role ──────────────────────────────────────────────────────────────────
class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleOut(RoleBase):
    id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Permission ────────────────────────────────────────────────────────────
class PermissionOut(BaseModel):
    id: uuid.UUID
    resource: str
    can_create: bool
    can_read: bool
    can_update: bool
    can_delete: bool

    model_config = {"from_attributes": True}


# ── Admin ─────────────────────────────────────────────────────────────────
class AdminCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=150)
    role_id: Optional[uuid.UUID] = None


class AdminUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None


class AdminOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    avatar_url: Optional[str]
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    role: Optional[RoleOut]

    model_config = {"from_attributes": True}


# ── Auth ──────────────────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
