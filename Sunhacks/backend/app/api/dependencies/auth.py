from __future__ import annotations

import os

from fastapi import HTTPException
from fastapi import Request


def resolve_authenticated_user_id(request: Request) -> str:
    user_id = getattr(request.state, "authenticated_user_id", None)
    if user_id:
        return str(user_id)

    if os.getenv("APP_ENV", "development") != "production":
        return "user-local"

    raise HTTPException(status_code=401, detail="Authenticated user identity is required")
