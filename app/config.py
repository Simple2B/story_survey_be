from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    SERVER_NAME: str = "StorySurvey"
    SAMPLE_ENV_VAR: str = "sample_env_var_test"
    JWT_SECRET: str = "jwt_secret_test"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URI: str = ""
    DEV_DATABASE_URI: str = "sqlite:///./test.db"
    ADMIN_USER: str = "admin"
    ADMIN_PASS: str = "admin"
    ADMIN_EMAIL: EmailStr = "admin@admin.com"

    class Config:
        env_file = ".env"


settings = Settings()
