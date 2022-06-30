from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import model, schema

# from app import schema
# from app.config import settings


def test_stripe_callback(client: TestClient, db: Session):
    pass
    # key = settings.BASIC_PRICE_LOOKUP_KEY
    # data = schema.StripeData(email="admin@gmail.com", key=key)

    # response = client.post("/backend/stripe/", json=data.dict())
    # assert response


def test_create_stripe_customer(client: TestClient, db: Session):
    USER_EMAIL = "vsabybina7@gmail.com"
    CUSTOMER_ID = "cu_64764784"
    data = schema.CreateCustomer(email=USER_EMAIL, stripe_customer=CUSTOMER_ID)

    # create stripe customer
    response = client.post("/backend/stripe/create_customer", json=data.dict())
    assert response.ok
    assert response.json()["email"] == data.email

    # check that data has been added to stripe_data model
    user = db.query(model.User).filter(model.User.email == data.email).first()
    user_stripe_data = (
        db.query(model.Stripe).filter(model.Stripe.id == user.stripe_data_id).first()
    )
    assert user_stripe_data.stripe_customer_id == data.stripe_customer
