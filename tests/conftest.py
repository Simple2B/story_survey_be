import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app import schema


@pytest.fixture
def client() -> Generator:

    with TestClient(app) as c:
        yield c


@pytest.fixture
def db() -> Generator:
    # SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
    SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db:

        def override_get_db() -> Generator:
            yield db

        app.dependency_overrides[get_db] = override_get_db

        yield db
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def stripe_data_helper() -> Generator:
    USER_EMAIL = "vsabybina7@gmail.com"
    CUSTOMER_ID = "cu_64764784"
    BASIC_PRODUCT_KEY = "price_1LFwQJCMiCKtiI680YEDDamf"
    SESSION_ID = "su_gjhg3t88"
    SUBSCRIPTION_ID = "sub_jhg2538"
    data = schema.StripeData(
        email=USER_EMAIL,
        stripe_customer=CUSTOMER_ID,
        basic_product_key=BASIC_PRODUCT_KEY,
        stripe_session_id=SESSION_ID,
        subscription_id=SUBSCRIPTION_ID,
    )

    yield data
