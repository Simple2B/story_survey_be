from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import schema
from app.config import settings


def test_stripe_callback(client: TestClient, db: Session):
    pass
    # key = settings.BASIC_PRICE_LOOKUP_KEY
    # data = schema.StripeData(email="admin@gmail.com", key=key)

    # response = client.post("/backend/stripe/", json=data.dict())
    # assert response
