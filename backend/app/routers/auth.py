import secrets

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.auth import create_access_token, get_current_user, verify_password
from app.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

_COOKIE_NAME = "access_token"


def _cookie_max_age() -> int:
    return settings.access_token_expire_hours * 3600


class UserInfo(BaseModel):
    username: str


@router.post("/login")
def login(response: Response, form: OAuth2PasswordRequestForm = Depends()):
    """Authenticate with username + password; sets a secure httpOnly cookie."""
    if not settings.auth_password_hash:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Authentication not configured. Set AUTH_PASSWORD_HASH in your .env file. "
                "Generate with: "
                "python -c \"import bcrypt; print(bcrypt.hashpw(b'yourpassword', bcrypt.gensalt(12)).decode())\""
            ),
        )

    # Always run both checks to prevent timing-based username enumeration.
    password_ok = verify_password(form.password, settings.auth_password_hash)
    username_ok = secrets.compare_digest(
        form.username.lower(), settings.auth_username.lower()
    )

    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token(form.username)
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="strict",
        secure=settings.cookie_secure,
        max_age=_cookie_max_age(),
        path="/",
    )
    return {"message": "Logged in successfully"}


@router.post("/logout")
def logout(response: Response):
    """Clear the auth cookie."""
    response.delete_cookie(key=_COOKIE_NAME, path="/", samesite="strict")
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserInfo)
def get_me(username: str = Depends(get_current_user)):
    """Return info about the currently authenticated user."""
    return UserInfo(username=username)
