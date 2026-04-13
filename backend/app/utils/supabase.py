"""
SportSkyline Backend — Supabase Client Utility (Stubbed)
This version avoids the 'supabase' python library to bypass Py3.14 build errors.
To be replaced with a lightweight httpx version.
"""
from loguru import logger
from app.config import settings

def get_supabase_client():
    """Stubbed - avoiding supabase-py library."""
    logger.warning("Supabase Client is currently stubbed due to library build issues.")
    return None


async def upload_to_supabase(file_content: bytes, filename: str, content_type: str) -> str:
    """
    STUB - Returns a local placeholder URL.
    To be replaced with a raw HTTP implementation using httpx.
    """
    logger.error(f"Cannot upload {filename}: Supabase library is currently disabled.")
    return f"https://placeholder.com/stubs/{filename}"
