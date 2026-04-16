from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql://tuxplanner:tuxplanner@localhost:5432/tuxplanner"

    class Config:
        env_file = ".env"


settings = Settings()
