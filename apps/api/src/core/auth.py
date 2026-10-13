import time
from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any, cast

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from jose.exceptions import JWTError

from src.core.config import settings

_security = HTTPBearer()
_JWKS_TTL_SECONDS = 3600
_jwks_cache: dict[str, Any] = {"keys": None, "fetched_at": 0.0}


async def _get_jwks() -> dict[str, Any]:
    now = time.time()
    if _jwks_cache["keys"] is None or now - _jwks_cache["fetched_at"] > _JWKS_TTL_SECONDS:
        url = (
            f"https://login.microsoftonline.com/{settings.entra_tenant_id}"
            "/discovery/v2.0/keys"
        )
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
        _jwks_cache["keys"] = response.json()
        _jwks_cache["fetched_at"] = now
    return cast(dict[str, Any], _jwks_cache["keys"])


@dataclass
class CurrentOfficer:
    email: str
    roles: list[str]


async def get_current_officer(
    credentials: HTTPAuthorizationCredentials = Depends(_security),
) -> CurrentOfficer:
    token = credentials.credentials
    jwks = await _get_jwks()
    try:
        header = jwt.get_unverified_header(token)
        signing_key = next(
            (key for key in jwks["keys"] if key["kid"] == header.get("kid")), None
        )
        if signing_key is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown signing key"
            )
        claims = jwt.decode(
            token,
            signing_key,
            algorithms=["RS256"],
            audience=settings.entra_client_id,
            issuer=f"https://login.microsoftonline.com/{settings.entra_tenant_id}/v2.0",
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from exc

    email = claims.get("preferred_username") or claims.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing email claim"
        )
    return CurrentOfficer(email=email, roles=claims.get("roles", []))


def require_role(
    *allowed_roles: str,
) -> Callable[[CurrentOfficer], Coroutine[Any, Any, CurrentOfficer]]:
    async def _guard(
        officer: CurrentOfficer = Depends(get_current_officer),
    ) -> CurrentOfficer:
        if not any(role in officer.roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient role"
            )
        return officer

    return _guard
