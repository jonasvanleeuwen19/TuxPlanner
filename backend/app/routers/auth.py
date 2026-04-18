import secrets

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth import create_access_token, get_current_user
from app.config import settings
from app.database import get_db
from app.models import User

router = APIRouter(prefix="/auth", tags=["auth"])

_COOKIE_NAME = "access_token"


def _cookie_max_age() -> int:
    return settings.access_token_expire_hours * 3600


class UserInfo(BaseModel):
    username: str
    is_admin: bool


class SetupRequest(BaseModel):
    username: str
    password: str


@router.get("/setup-status")
def setup_status(db: Session = Depends(get_db)):
    """Return whether the first-run setup has been completed (any user exists)."""
    has_users = db.query(User).first() is not None
    return {"setup_required": not has_users}


@router.post("/setup", status_code=status.HTTP_201_CREATED)
def setup(body: SetupRequest, response: Response, db: Session = Depends(get_db)):
    """Create the first admin account. Only available before any user exists."""
    if db.query(User).first() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Setup has already been completed.",
        )

    if len(body.username.strip()) == 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username must not be empty.",
        )
    if len(body.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters.",
        )

    password_hash = bcrypt.hashpw(body.password.encode("utf-8"), bcrypt.gensalt(12)).decode()
    user = User(username=body.username.strip(), password_hash=password_hash, is_admin=True)
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.username)
    response.set_cookie(
        key=_COOKIE_NAME,
        value=token,
        httponly=True,
        samesite="strict",
        secure=settings.cookie_secure,
        max_age=_cookie_max_age(),
        path="/",
    )
    return {"message": "Account created and logged in successfully"}


@router.post("/login")
def login(response: Response, form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate with username + password; sets a secure httpOnly cookie."""
    if db.query(User).first() is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Setup not completed. Please create an account first.",
        )

    user = db.query(User).filter(User.username == form.username).first()

    # Always run bcrypt to prevent timing-based username enumeration.
    dummy_hash = "$2b$12$AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
    stored_hash = user.password_hash if user else dummy_hash
    try:
        password_ok = bcrypt.checkpw(form.password.encode("utf-8"), stored_hash.encode("utf-8"))
    except Exception:
        password_ok = False

    username_ok = user is not None and secrets.compare_digest(
        form.username.lower(), user.username.lower()
    )

    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    token = create_access_token(user.username)
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
def get_me(username: str = Depends(get_current_user), db: Session = Depends(get_db)):
    """Return info about the currently authenticated user."""
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserInfo(username=user.username, is_admin=user.is_admin)
