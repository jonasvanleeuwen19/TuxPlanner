import logging
import os
import secrets

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

_PLACEHOLDER = "CHANGE_ME_BEFORE_DEPLOY_use_openssl_rand_hex_32"
# File used to persist an auto-generated key across restarts.
_KEY_FILE = ".secret_key"


class Settings(BaseSettings):
    database_url: str = "postgresql://tuxplanner:tuxplanner@localhost:5432/tuxplanner"

    # ── Auth ─────────────────────────────────────────────────────
    # If left as the placeholder, a secure key is generated automatically
    # and persisted to .secret_key so it survives restarts.
    secret_key: str = _PLACEHOLDER
    access_token_expire_hours: int = 8
    # Set to True in production when running behind HTTPS
    cookie_secure: bool = False

    model_config = SettingsConfigDict(env_file=".env")

    @model_validator(mode="after")
    def _auto_generate_secret_key(self) -> "Settings":
        """Generate a secure random key when the placeholder is detected."""
        if self.secret_key != _PLACEHOLDER:
            return self

        key_file = os.path.abspath(_KEY_FILE)
        if os.path.exists(key_file):
            with open(key_file, encoding="utf-8") as f:
                self.secret_key = f.read().strip()
            logger.info("Loaded auto-generated secret key from %s", key_file)
        else:
            self.secret_key = secrets.token_hex(32)
            try:
                # Create with restrictive permissions (owner read/write only).
                fd = os.open(key_file, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    f.write(self.secret_key)
                logger.info(
                    "Generated new secret key and saved to %s. "
                    "Set SECRET_KEY in your environment to use a fixed key.",
                    key_file,
                )
            except OSError as exc:
                logger.warning(
                    "Could not persist auto-generated secret key to %s: %s. "
                    "All sessions will be invalidated on restart.",
                    key_file,
                    exc,
                )

        return self


settings = Settings()
