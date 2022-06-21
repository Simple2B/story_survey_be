import datetime
from app import schema


def create_user():
    USER_NAME = "VASYL"
    USER_EMAIL = "test@test.ku"
    USER_PASSWORD = "secret"
    data = schema.UserCreate(
        username=USER_NAME,
        email=USER_EMAIL,
        password=USER_PASSWORD,
    )
    return data
