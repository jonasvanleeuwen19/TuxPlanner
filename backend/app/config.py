from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://tuxplanner:tuxplanner@localhost:5432/tuxplanner"

    # ── Auth ─────────────────────────────────────────────────────
    # Generate a strong key with: openssl rand -hex 32
    secret_key: str = "CHANGE_ME_BEFORE_DEPLOY_use_openssl_rand_hex_32"
    access_token_expire_hours: int = 8
    auth_username: str = "admin"
    # Generate hash with:
    #   python -c "import bcrypt; print(bcrypt.hashpw(b'yourpassword', bcrypt.gensalt(12)).decode())"
    auth_password_hash: str = ""
    # Set to True in production when running behind HTTPS
    cookie_secure: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
