from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.officer import Officer


class OfficerNotFoundError(ValueError):
    pass


async def find_officer_by_name(session: AsyncSession, name: str) -> Officer | None:
    stmt = select(Officer).where(Officer.name.ilike(f"%{name}%"))
    result = await session.execute(stmt)
    return result.scalars().first()


async def resolve_attendee_emails(session: AsyncSession, names: list[str]) -> list[str]:
    emails: list[str] = []
    for name in names:
        if "@" in name:
            # Already an email address (e.g. user typed it directly) — nothing
            # to resolve, the officers table only maps free-text names -> email.
            emails.append(name)
            continue
        officer = await find_officer_by_name(session, name)
        if officer is None:
            raise OfficerNotFoundError(f"No officer found matching '{name}'")
        emails.append(officer.email)
    return emails
