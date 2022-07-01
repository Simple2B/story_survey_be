from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import model, schema

# from app import schema
# from app.config import settings


def test_create_customer(client: TestClient, db: Session):
    USER_EMAIL = "vsabybina7@gmail.com"
    CUSTOMER_ID = "cu_64764784"
    data = schema.CreateCustomer(email=USER_EMAIL, stripe_customer=CUSTOMER_ID)

    # create stripe customer
    response = client.post("/backend/stripe/create_customer", json=data.dict())
    assert response.ok
    response_data = response.json()
    assert response_data["customer_id"] == data.stripe_customer

    # check that data has been added to stripe_data model
    customer_data = (
        db.query(model.Stripe)
        .filter(model.Stripe.user_id == response_data["id"])
        .first()
    )
    assert customer_data.customer_id == data.stripe_customer
