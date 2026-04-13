"""
SportSkyline Backend — Pydantic v2 Schemas: Ads, Banners, Media, Settings, Audit
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field


# ── Banner ────────────────────────────────────────────────────────────────
class BannerCreate(BaseModel):
    name: str = Field(..., max_length=200)
    placement: str
    image_url: str
    link_url: Optional[str] = None
    target_blank: bool = True
    is_active: bool = True
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BannerUpdate(BaseModel):
    name: Optional[str] = None
    placement: Optional[str] = None
    image_url: Optional[str] = None
    link_url: Optional[str] = None
    target_blank: Optional[bool] = None
    is_active: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BannerOut(BaseModel):
    id: uuid.UUID
    name: str
    placement: str
    image_url: str
    link_url: Optional[str]
    target_blank: bool
    is_active: bool
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    impression_count: int
    click_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Media Asset ───────────────────────────────────────────────────────────
class MediaAssetOut(BaseModel):
    id: uuid.UUID
    filename: str
    original_name: Optional[str]
    url: str
    mime_type: Optional[str]
    size_bytes: Optional[int]
    width: Optional[int]
    height: Optional[int]
    alt_text: Optional[str]
    caption: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class MediaAssetUpdate(BaseModel):
    alt_text: Optional[str] = None
    caption: Optional[str] = None


# ── App Setting ───────────────────────────────────────────────────────────
class SettingOut(BaseModel):
    id: uuid.UUID
    key: str
    value: Optional[str]
    value_type: str
    description: Optional[str]
    is_public: bool
    updated_at: datetime

    model_config = {"from_attributes": True}


class SettingUpdate(BaseModel):
    value: Any


# ── Audit Log ─────────────────────────────────────────────────────────────
class AuditLogOut(BaseModel):
    id: uuid.UUID
    admin_id: Optional[uuid.UUID]
    action: str
    resource: Optional[str]
    resource_id: Optional[uuid.UUID]
    old_data: Optional[dict]
    new_data: Optional[dict]
    ip_address: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Homepage Block ────────────────────────────────────────────────────────
class HomepageBlockCreate(BaseModel):
    section_id: uuid.UUID
    article_id: Optional[uuid.UUID] = None
    match_id: Optional[uuid.UUID] = None
    block_type: str = "article"
    sort_order: int = 0
    custom_title: Optional[str] = None
    custom_subtitle: Optional[str] = None
    is_active: bool = True
    valid_until: Optional[datetime] = None


class HomepageBlockOut(BaseModel):
    id: uuid.UUID
    section_id: uuid.UUID
    article_id: Optional[uuid.UUID]
    match_id: Optional[uuid.UUID]
    block_type: str
    sort_order: int
    custom_title: Optional[str]
    custom_subtitle: Optional[str]
    is_active: bool
    valid_until: Optional[datetime]
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Pagination ────────────────────────────────────────────────────────────
class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int
