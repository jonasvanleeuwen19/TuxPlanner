from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Cookie, HTTPException, status

from app.config import settings

_ALGORITHM = "HS256"


def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plaintext password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def create_access_token(subject: str) -> str:
    """Create a signed JWT access token for *subject* (username)."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(hours=settings.access_token_expire_hours)
    payload = {"sub": subject, "iat": now, "exp": expire}
    return jwt.encode(payload, settings.secret_key, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    """Decode and verify a JWT; return the *sub* claim or None on failure."""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[_ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


def get_current_user(access_token: Optional[str] = Cookie(default=None)) -> str:
    """FastAPI dependency – raises 401 if the request is not authenticated."""
    username = decode_access_token(access_token) if access_token else None
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username
