from app import schema


def create_user(name: str = "Poll", email: str = "test@test.ku"):
    USER_NAME = name
    USER_EMAIL = email
    USER_PASSWORD = "secret"
    data = schema.UserCreate(
        username=USER_NAME,
        email=USER_EMAIL,
        password=USER_PASSWORD,
    )
    return data
