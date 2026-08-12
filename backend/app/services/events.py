"""System event logging helper."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.system_event import SystemEvent


async def log_event(
    db: AsyncSession,
    event_type: str,
    message: str,
    verification_id: UUID | None = None,
) -> None:
    db.add(
        SystemEvent(
            event_type=event_type,
            message=message[:2000],
            verification_id=verification_id,
        )
    )
