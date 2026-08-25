"""Authentication for the administration endpoints.

The admin routes expose session metadata (identifiers, timestamps, message
counts) and allow sessions to be destroyed. For a service used by victims of
cyberviolence that surface must never be reachable anonymously once the API is
deployed publicly.

Policy:
  * `ADMIN_API_KEY` unset  -> the endpoints answer **404**, exactly as if they
    did not exist. Not configuring the key is therefore the safe default: an
    accidental public deployment exposes nothing and leaks no hint that an admin
    surface exists at all.
  * `ADMIN_API_KEY` set    -> the `X-Admin-Key` header is required and compared
    in constant time.
"""
import secrets
from typing import Optional

from fastapi import Header, HTTPException, status

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
# Imported as a module (not `from config import ...`) so the value is read at
# request time and can be overridden in tests.
import config

ADMIN_KEY_HEADER = "X-Admin-Key"


async def require_admin_key(
    x_admin_key: Optional[str] = Header(default=None, alias=ADMIN_KEY_HEADER),
) -> None:
    """FastAPI dependency guarding every admin route."""
    configured_key = getattr(config, "ADMIN_API_KEY", None)

    if not configured_key:
        # Do not reveal that the route exists.
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Found",
        )

    if not x_admin_key or not secrets.compare_digest(x_admin_key, configured_key):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé d'administration invalide ou absente.",
            headers={"WWW-Authenticate": ADMIN_KEY_HEADER},
        )
