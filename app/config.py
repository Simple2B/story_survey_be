from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    SERVER_NAME: str = "StorySurvey"
    SAMPLE_ENV_VAR: str = "sample_env_var_test"
    JWT_SECRET: str = "jwt_secret_test"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URI: str = ""
    DEV_DATABASE_URI: str = "sqlite:///./test.db"
    ADMIN_USER: str = "Varvara"
    ADMIN_PASS: str = "admin"
    ADMIN_EMAIL: EmailStr = "vsabybina7@gmail.com"

    ADMIN2_USER: str = "Steve"
    ADMIN2_PASS: str = "admin"
    ADMIN2_EMAIL: EmailStr = "steve@pogol.net"

    ADMIN3_USER: str = "Dmytriy"
    ADMIN3_PASS: str = "admin"
    ADMIN3_EMAIL: EmailStr = "danylov.dmytro@gmail.com"

    STRIPE_PUBLIC_KEY: str = "pk_secret"
    STRIPE_SECRET_KEY: str = "sk_secret"
    BASIC_PRICE_LOOKUP_KEY: str = "basic_product_price_key"
    ADVANCE_PRICE_LOOKUP_KEY: str = "advance_product_price_key"

    class Config:
        env_file = ".env"


settings = Settings()
