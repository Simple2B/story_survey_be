from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import model, schema

# from app import schema
# from app.config import settings


def test_create_customer(client: TestClient, db: Session):
    pass
    # """Test for function create_customer() from router/stripe.py"""
    # USER_EMAIL = "vsabybina7@gmail.com"
    # CUSTOMER_ID = "cu_64764784"
    # data = schema.CreateCustomer(email=USER_EMAIL, stripe_customer=CUSTOMER_ID)

    # # create stripe customer
    # response = client.post("/backend/stripe/create_customer", json=data.dict())
    # assert response.ok
    # response_data = response.json()
    # assert response_data["customer_id"] == data.stripe_customer

    # # check that data has been added to stripe_data model
    # customer_data = (
    #     db.query(model.Stripe)
    #     .filter(model.Stripe.user_id == response_data["id"])
    #     .first()
    # )
    # assert customer_data.customer_id == data.stripe_customer


def test_create_sessionr(client: TestClient, db: Session):
    """
    Test for function create_stripe_session() from router/stripe.py
    """

    USER_EMAIL = "vsabybina7@gmail.com"
    CUSTOMER_ID = "cu_64764784"
    BASIC_PRODUCT_KEY = "price_1LFwQJCMiCKtiI680YEDDamf"
    SESSION_ID = "su_gjhg3t88"
    data = schema.StripeData(
        email=USER_EMAIL,
        stripe_customer=CUSTOMER_ID,
        basic_product_key=BASIC_PRODUCT_KEY,
        stripe_session_id=SESSION_ID,
    )

    # create stripe customer
    data_for_create = schema.CreateCustomer(
        email=USER_EMAIL, stripe_customer=CUSTOMER_ID
    )
    response = client.post(
        "/backend/stripe/create_customer", json=data_for_create.dict()
    )
    assert response.ok

    # send session data
    response = client.post("/backend/stripe/create_stripe_session", json=data.dict())
    assert response.ok
    response_data = response.json()
    assert response_data["session_id"] == data.stripe_session_id

    # check inserted data in stripe_data model
    session_data = (
        db.query(model.Stripe)
        .filter(model.Stripe.user_id == response_data["id"])
        .first()
    )
    assert session_data.session_id == data.stripe_session_id
    assert session_data.subscription == model.Stripe.SubscriptionType.Basic
