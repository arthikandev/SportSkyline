"""
SportSkyline Backend — Utility: Slug Generator
Generates URL-safe slugs with uniqueness checking.
"""
import re
import uuid
from typing import Callable, Awaitable, Optional


def slugify(text: str) -> str:
    """Convert text to lowercase URL-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text


async def unique_slug(
    base_text: str,
    exists_fn: Callable[[str], Awaitable[bool]],
    max_length: int = 480,
) -> str:
    """
    Generate a unique slug. If the base slug already exists,
    appends a short uuid suffix.
    
    Args:
        base_text: The title / text to slugify.
        exists_fn: Async function that returns True if slug already exists.
        max_length: Maximum slug length.
    """
    slug = slugify(base_text)[:max_length]
    if not await exists_fn(slug):
        return slug

    # Append short UUID suffix and retry
    suffix = str(uuid.uuid4())[:8]
    candidate = f"{slug[:max_length - 9]}-{suffix}"
    return candidate
