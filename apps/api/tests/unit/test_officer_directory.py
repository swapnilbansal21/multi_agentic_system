from __future__ import annotations

import pytest
from sqlalchemy import delete

from src.db.session import async_session_factory
from src.models.officer import Officer
from src.services.officer_directory import (
    OfficerNotFoundError,
    find_officer_by_name,
    resolve_attendee_emails,
)

TEST_EMAIL = "rakesh.kumar@test.example"


async def _cleanup() -> None:
    async with async_session_factory() as session:
        await session.execute(delete(Officer).where(Officer.email == TEST_EMAIL))
        await session.commit()


@pytest.mark.asyncio
async def test_find_officer_by_name_case_insensitive_partial_match() -> None:
    async with async_session_factory() as session:
        session.add(Officer(name="Rakesh Kumar", email=TEST_EMAIL))
        await session.commit()

    try:
        async with async_session_factory() as session:
            officer = await find_officer_by_name(session, "rakesh")
            assert officer is not None
            assert officer.email == TEST_EMAIL
    finally:
        await _cleanup()


@pytest.mark.asyncio
async def test_find_officer_by_name_no_match_returns_none() -> None:
    async with async_session_factory() as session:
        officer = await find_officer_by_name(session, "no-such-officer-xyz")
        assert officer is None


@pytest.mark.asyncio
async def test_resolve_attendee_emails_success() -> None:
    async with async_session_factory() as session:
        session.add(Officer(name="Rakesh Kumar", email=TEST_EMAIL))
        await session.commit()

    try:
        async with async_session_factory() as session:
            emails = await resolve_attendee_emails(session, ["rakesh"])
            assert emails == [TEST_EMAIL]
    finally:
        await _cleanup()


@pytest.mark.asyncio
async def test_resolve_attendee_emails_raises_when_not_found() -> None:
    async with async_session_factory() as session:
        with pytest.raises(OfficerNotFoundError):
            await resolve_attendee_emails(session, ["no-such-officer-xyz"])


@pytest.mark.asyncio
async def test_resolve_attendee_emails_passes_through_raw_emails() -> None:
    async with async_session_factory() as session:
        emails = await resolve_attendee_emails(session, ["already.an.email@example.com"])
        assert emails == ["already.an.email@example.com"]


@pytest.mark.asyncio
async def test_resolve_attendee_emails_mixes_names_and_emails() -> None:
    async with async_session_factory() as session:
        session.add(Officer(name="Rakesh Kumar", email=TEST_EMAIL))
        await session.commit()

    try:
        async with async_session_factory() as session:
            emails = await resolve_attendee_emails(
                session, ["rakesh", "raw.email@example.com"]
            )
            assert emails == [TEST_EMAIL, "raw.email@example.com"]
    finally:
        await _cleanup()
