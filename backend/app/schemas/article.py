"""
SportSkyline Backend — Pydantic v2 Schemas: Articles, Categories, Tags, Authors
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ── Category ──────────────────────────────────────────────────────────────
class CategoryBase(BaseModel):
    name: str = Field(..., max_length=150)
    description: Optional[str] = None
    color: Optional[str] = None
    sort_order: int = 0
    is_active: bool = True
    sport_id: Optional[uuid.UUID] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    sort_order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryOut(CategoryBase):
    id: uuid.UUID
    slug: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Tag ───────────────────────────────────────────────────────────────────
class TagCreate(BaseModel):
    name: str = Field(..., max_length=100)


class TagOut(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Author ────────────────────────────────────────────────────────────────
class AuthorCreate(BaseModel):
    display_name: str = Field(..., max_length=150)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    admin_id: Optional[uuid.UUID] = None


class AuthorOut(BaseModel):
    id: uuid.UUID
    display_name: str
    bio: Optional[str]
    avatar_url: Optional[str]
    twitter_handle: Optional[str]

    model_config = {"from_attributes": True}


# ── Article ───────────────────────────────────────────────────────────────
class ArticleCreate(BaseModel):
    title: str = Field(..., max_length=500)
    excerpt: Optional[str] = None
    content: str
    featured_image_url: Optional[str] = None
    image_credit: Optional[str] = None
    sport_id: Optional[uuid.UUID] = None
    category_id: Optional[uuid.UUID] = None
    author_id: Optional[uuid.UUID] = None
    status: str = "draft"
    is_featured: bool = False
    is_trending: bool = False
    is_breaking: bool = False
    is_hero: bool = False
    read_time_minutes: int = 5
    scheduled_at: Optional[datetime] = None
    tag_ids: List[uuid.UUID] = []
    # SEO
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    excerpt: Optional[str] = None
    content: Optional[str] = None
    featured_image_url: Optional[str] = None
    image_credit: Optional[str] = None
    sport_id: Optional[uuid.UUID] = None
    category_id: Optional[uuid.UUID] = None
    author_id: Optional[uuid.UUID] = None
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    is_trending: Optional[bool] = None
    is_breaking: Optional[bool] = None
    is_hero: Optional[bool] = None
    read_time_minutes: Optional[int] = None
    scheduled_at: Optional[datetime] = None
    tag_ids: Optional[List[uuid.UUID]] = None
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: Optional[str] = None


class ArticleListOut(BaseModel):
    """Compact article for lists/feeds."""
    id: uuid.UUID
    title: str
    slug: str
    excerpt: Optional[str]
    featured_image_url: Optional[str]
    status: str
    is_featured: bool
    is_trending: bool
    is_breaking: bool
    is_hero: bool
    view_count: int
    read_time_minutes: int
    published_at: Optional[datetime]
    created_at: datetime
    sport_id: Optional[uuid.UUID]
    category: Optional[CategoryOut]
    author: Optional[AuthorOut]
    tags: List[TagOut] = []

    model_config = {"from_attributes": True}


class ArticleDetailOut(ArticleListOut):
    """Full article with content."""
    content: str
    image_credit: Optional[str]
    seo_title: Optional[str]
    seo_description: Optional[str]
    seo_keywords: Optional[str]
    updated_at: datetime

    model_config = {"from_attributes": True}


class ScheduleRequest(BaseModel):
    scheduled_at: datetime
