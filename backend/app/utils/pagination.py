"""
SportSkyline Backend — Utility: Pagination
"""
import math
from typing import TypeVar, Generic, List, Optional, Any
from pydantic import BaseModel

T = TypeVar("T")


class PageParams(BaseModel):
    page: int = 1
    page_size: int = 10

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    def clamp(self, max_size: int = 100) -> "PageParams":
        return PageParams(
            page=max(1, self.page),
            page_size=min(max(1, self.page_size), max_size),
        )


def paginate(items: List[Any], total: int, page: int, page_size: int) -> dict:
    """Build paginated response dict."""
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": math.ceil(total / page_size) if page_size > 0 else 1,
    }
