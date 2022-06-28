from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import model, schema
from .helper import create_user


def test_stripe_callback(client: TestClient, db: Session):
    data = schema.StripeData(email="admin@gmail.com")

    response = client.post("/backend/stripe/", json=data.dict())
    assert response
