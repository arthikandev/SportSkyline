"""
SportSkyline Backend — Middleware: Role-Based Access Control (RBAC)
"""
from functools import wraps
from typing import Callable, List

from fastapi import Depends, HTTPException, status

from app.middleware.auth import get_current_admin
from app.models.admin import Admin


def require_role(*allowed_roles: str) -> Callable:
    """
    FastAPI dependency factory that checks if the current admin
    has one of the allowed role names.
    
    Usage:
        @router.delete("/{id}", dependencies=[Depends(require_role("super_admin"))])
    """
    async def _checker(admin: Admin = Depends(get_current_admin)) -> Admin:
        if not admin.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No role assigned to this admin",
            )
        if admin.role.name not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role '{admin.role.name}' is not allowed for this action. Required: {allowed_roles}",
            )
        return admin
    return _checker


# Convenience role dependencies
def require_super_admin():
    return require_role("super_admin")

def require_editor_or_above():
    return require_role("super_admin", "editor")

def require_any_role():
    return require_role("super_admin", "editor", "moderator")
