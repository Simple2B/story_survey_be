from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import model, schema


def test_create_customer(
    client: TestClient, db: Session, stripe_data_helper: schema.StripeData
):
    """Test for function create_customer() from router/stripe.py"""

    data = schema.CreateOrDeleteCustomer(
        email=stripe_data_helper.email,
        stripe_customer=stripe_data_helper.stripe_customer,
    )

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


def test_delete_customer(
    client: TestClient, db: Session, stripe_data_helper: schema.StripeData
):
    """Test for function delete_stripe_customer() from router/stripe.py"""
    # create stripe customer
    customer_data = schema.CreateOrDeleteCustomer(
        email=stripe_data_helper.email,
        stripe_customer=stripe_data_helper.stripe_customer,
    )
    response = client.post("/backend/stripe/create_customer", json=customer_data.dict())
    assert response.ok

    # delete customer
    response = client.delete(
        "/backend/stripe/delete_customer", json=customer_data.dict()
    )
    assert response.status_code == 204

    # check existance of deleted customer in database
    customer = (
        db.query(model.Stripe)
        .filter(
            model.Stripe.customer_id == customer_data.stripe_customer,
            model.Stripe.session_id == None,
        )
        .first()
    )
    assert customer == None


def test_create_session(
    client: TestClient, db: Session, stripe_data_helper: schema.StripeData
):
    """
    Test for function create_stripe_session() from router/stripe.py
    """

    # create stripe customer
    data_for_create = schema.CreateOrDeleteCustomer(
        email=stripe_data_helper.email,
        stripe_customer=stripe_data_helper.stripe_customer,
    )
    response = client.post(
        "/backend/stripe/create_customer", json=data_for_create.dict()
    )
    assert response.ok

    # send session data
    response = client.post(
        "/backend/stripe/create_stripe_session", json=stripe_data_helper.dict()
    )
    assert response.ok
    response_data = response.json()
    assert response_data["session_id"] == stripe_data_helper.stripe_session_id

    # check inserted data in stripe_data model
    session_data = (
        db.query(model.Stripe)
        .filter(model.Stripe.user_id == response_data["id"])
        .first()
    )
    assert session_data.session_id == stripe_data_helper.stripe_session_id
    assert session_data.subscription == model.Stripe.SubscriptionType.Basic


def test_create_subscription(
    client: TestClient, db: Session, stripe_data_helper: schema.StripeData
):
    """
    Test for function create_subscription() from router/stripe.py
    """
    # create new stripe customer
    customer_data = schema.CreateOrDeleteCustomer(
        email=stripe_data_helper.email,
        stripe_customer=stripe_data_helper.stripe_customer,
    )
    response = client.post("/backend/stripe/create_customer", json=customer_data.dict())
    assert response.ok

    # create user's stripe session
    response = client.post(
        "/backend/stripe/create_stripe_session", json=stripe_data_helper.dict()
    )
    assert response.ok

    # create subscription
    subscription_data = schema.StripeSubscription(
        email=stripe_data_helper.email,
        stripe_customer=stripe_data_helper.stripe_customer,
        subscription_id=stripe_data_helper.subscription_id,
    )
    response = client.post(
        "/backend/stripe/create_subscription", json=subscription_data.dict()
    )
    assert response.ok
    response_data = response.json()
    assert response_data["stripe_customer"] == stripe_data_helper.stripe_customer
    assert response_data["subscription_id"] == subscription_data.subscription_id


def test_delete_subscription(
    client: TestClient, db: Session, stripe_data_helper: schema.StripeData
):
    """
    Test for function delete_subscription() from router/stripe.py
    """
    # create new stripe customer
    customer_data = schema.CreateOrDeleteCustomer(
        email=stripe_data_helper.email,
        stripe_customer=stripe_data_helper.stripe_customer,
    )
    response = client.post("/backend/stripe/create_customer", json=customer_data.dict())
    assert response.ok

    # create user's stripe session
    response = client.post(
        "/backend/stripe/create_stripe_session", json=stripe_data_helper.dict()
    )
    assert response.ok

    # create subscription
    subscription_data = schema.StripeSubscription(
        email=stripe_data_helper.email,
        stripe_customer=stripe_data_helper.stripe_customer,
        subscription_id=stripe_data_helper.subscription_id,
    )
    response = client.post(
        "/backend/stripe/create_subscription", json=subscription_data.dict()
    )
    assert response.ok

    # delete subscription
    response = client.post(
        "/backend/stripe/delete_subscription",
        json=subscription_data.dict(),
    )
    assert response.status_code == 204

    # check existance of deleted data
    data = (
        db.query(model.Stripe)
        .filter(model.Stripe.subscription_id == subscription_data.subscription_id)
        .first()
    )
    assert data == None
