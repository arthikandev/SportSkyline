"""
SportSkyline Backend — Admin Router: Media & Ads
/api/v1/admin/ads/*
"""
import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_admin
from app.middleware.rbac import require_editor_or_above
from app.models.admin import Admin
from app.models.ad import Banner, MediaAsset
from app.schemas.system import BannerCreate, BannerUpdate, BannerOut, MediaAssetOut

router = APIRouter(prefix="/admin", tags=["Admin – Media & Ads"])


@router.get("/banners", response_model=List[BannerOut])
async def list_banners(
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    result = await db.execute(select(Banner).order_by(Banner.created_at.desc()))
    return result.scalars().all()


@router.post("/banners", response_model=BannerOut, status_code=201)
async def create_banner(
    payload: BannerCreate,
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_editor_or_above())
):
    banner = Banner(**payload.model_dump())
    db.add(banner)
    await db.flush()
    return banner


from app.utils.supabase import upload_to_supabase

@router.post("/media/upload", response_model=MediaAssetOut)
async def upload_media(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    admin: Admin = Depends(require_editor_or_above())
):
    """Uploads a file to Supabase Storage and records it in the database."""
    content = await file.read()
    
    # Upload to Supabase
    try:
        public_url = await upload_to_supabase(
            content, 
            file.filename, 
            file.content_type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    asset = MediaAsset(
        uploaded_by=admin.id,
        filename=file.filename,
        original_name=file.filename,
        url=public_url,
        storage_path=f"media/{file.filename}",
        mime_type=file.content_type,
        size_bytes=len(content)
    )
    db.add(asset)
    await db.flush()
    return asset
