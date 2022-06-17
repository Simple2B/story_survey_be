from app import schema


def create_user():
    USER_NAME = "VASYL"
    USER_EMAIL = "test@test.ku"
    USER_PASSWORD = "secret"
    FIRST_NAME = "Vasyl"
    LAST_NAME = "Hmura"
    # data = {"username": USER_NAME, "email": USER_EMAIL, "password": USER_PASSWORD}
    data = schema.UserCreate(
        first_name=FIRST_NAME,
        last_name=LAST_NAME,
        username=USER_NAME,
        email=USER_EMAIL,
        password=USER_PASSWORD,
    )
    return data
