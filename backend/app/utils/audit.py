"""
SportSkyline Backend — Utility: Audit Log Writer
"""
import uuid
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system import AuditLog


async def write_audit(
    db: AsyncSession,
    admin_id: Optional[uuid.UUID],
    action: str,
    resource: Optional[str] = None,
    resource_id: Optional[uuid.UUID] = None,
    old_data: Optional[dict] = None,
    new_data: Optional[dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> None:
    """
    Write an audit log entry to the database.
    Call this after any state-changing admin operation.
    """
    log = AuditLog(
        admin_id=admin_id,
        action=action,
        resource=resource,
        resource_id=resource_id,
        old_data=old_data,
        new_data=new_data,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    db.add(log)
    # Note: commit happens at the end of the request via get_db dependency
