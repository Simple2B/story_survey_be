from datetime import datetime
from fastapi import Depends, APIRouter, HTTPException, Response
from app import model, schema
from app.database import get_db
from sqlalchemy.orm import Session
from app.logger import log
from app.config import settings


router = APIRouter(prefix="/backend/stripe", tags=["Subscription"])
BASIC_PRICE_LOOKUP_KEY = settings.BASIC_PRICE_LOOKUP_KEY
ADVANCE_PRICE_LOOKUP_KEY = settings.ADVANCE_PRICE_LOOKUP_KEY


@router.post("/create_customer", response_model=schema.UserOut)
def create_stripe_customer(
    data: schema.CreateOrDeleteCustomer, db: Session = Depends(get_db)
):
    """
    This route insert customer_id in stripe_data model and return updated user's data.
    You should use this route when you create customer on Subscription platform and have to save his customer_id.
    """

    # check existance of user with such email
    user = db.query(model.User).filter(model.User.email == data.email).first()
    log(log.INFO, f"create_stripe_customer: user {data.email} exists: {bool(user)}")

    if not user:
        user = model.User(email=data.email)
        db.add(user)
        db.commit()
        db.refresh(user)
        log(
            log.INFO, f"create_stripe_customer: user {data.email} created: {bool(user)}"
        )

    # check existance of such customer_id
    stripe_customer = (
        db.query(model.Subscription)
        .filter(model.Subscription.customer_id == data.stripe_customer)
        .first()
    )

    if not stripe_customer:
        stripe_customer = model.Subscription(customer_id=data.stripe_customer)
        stripe_customer.user_id = user.id
        db.add(stripe_customer)
        db.commit()
        db.refresh(stripe_customer)
        log(
            log.INFO,
            f"create_stripe_customer: customer {data.stripe_customer} created: {bool(stripe_customer)}",
        )
        log(log.INFO, f"create_stripe_customer: for user {stripe_customer.user}")

    log(
        log.INFO,
        f"create_stripe_customer: customer {data.stripe_customer} exists: {bool(stripe_customer)}",
    )

    # return users data
    user_customer = schema.UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        role=user.role,
        image=user.image,
        customer_id=stripe_customer.customer_id,
    )
    return user_customer


@router.post("/delete_customer", status_code=204)
def delete_stripe_customer(data: schema.StripeCustomer, db: Session = Depends(get_db)):
    """
    This route deletes data in stripe_data model if row with accepted customer_id has no session_id.
    You can use it if user pressed "Cancel button" on Subscription type page.
    """
    if not data.customer_id:
        log(log.ERROR, "delete_customer: customer id doesn't exists")
        Response(status_code=404)

    # check existance of such customer_id
    stripe_customer = (
        db.query(model.Subscription)
        .filter(model.Subscription.customer_id == data.customer_id)
        .first()
    )

    if not stripe_customer:
        log(log.ERROR, "delete_customer: customer doesn't exists")
        Response(status_code=404)

    log(
        log.INFO,
        f"delete_customer: customer {data.customer_id} exists: {bool(stripe_customer)}",
    )

    db.delete(stripe_customer)
    db.commit()
    log(log.INFO, "delete_customer: customer was deleted")
    return Response(status_code=204)


@router.post("/create_stripe_session", response_model=schema.UserOut)
def create_stripe_session(data: schema.StripeSession, db: Session = Depends(get_db)):
    """
    This route inserts stripe data (session_d, subscription, product_id) into the stripe_data model
    You can use it when user creates stripe checkout session
    """

    # check existance of user
    user = db.query(model.User).filter_by(email=data.email).first()
    log(log.INFO, f"create_stripe_session: user {data.email} exists: {bool(user)}")

    if not user:
        log(log.ERROR, f"create_stripe_session: user {data.email} doesn't exists")
        raise HTTPException(status_code=404, detail="This user was not found")

    # check existance of such customer_id in model stripe_data
    stripe_data = (
        db.query(model.Subscription).filter_by(customer_id=data.stripe_customer).first()
    )

    if not stripe_data:
        stripe_data = model.Subscription(customer_id=data.stripe_customer)
        stripe_data.user_id = user.id
        db.add(stripe_data)
        db.commit()
        db.refresh(stripe_data)
        log(
            log.INFO,
            f"create_stripe_session: customer_id {data.stripe_customer} created: {bool(stripe_data)}",
        )
        log(log.INFO, f"create_stripe_session: for user {stripe_data.user}")
    log(
        log.INFO,
        f"create_stripe_session: customer_id {data.stripe_customer} exists: {bool(stripe_data)}",
    )

    # insert data into the stripe_data model
    stripe_data.session_id = data.stripe_session_id
    # stripe_data.subscription_id = data.subscription_id
    if data.product_key == BASIC_PRICE_LOOKUP_KEY:
        stripe_data.type = model.Subscription.SubscriptionType.Basic
        stripe_data.product_id = data.product_key
    if data.product_key == ADVANCE_PRICE_LOOKUP_KEY:
        stripe_data.type = model.Subscription.SubscriptionType.Advance
        stripe_data.product_id = data.product_key
    db.commit()
    db.refresh(stripe_data)
    log(
        log.INFO,
        f"create_stripe_session: data was inserted:\
            {stripe_data.session_id}, {stripe_data.product_id}",
    )
    log(log.INFO, f"create_stripe_session: for user {stripe_data.user}")

    # create my response
    my_response = schema.UserOut(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        role=user.role,
        image=user.image,
        customer_id=stripe_data.customer_id,
        session_id=stripe_data.session_id,
        # type=stripe_data.subscription,
        product_id=stripe_data.product_id,
    )

    return my_response


@router.post("/create_subscription", response_model=schema.StripeSubscription)
def create_subscription(data: schema.StripeSubscription, db: Session = Depends(get_db)):
    """
    This route inserts subscription_id into the stripe_data model
    """
    # check that such customer exists
    stripe_data = (
        db.query(model.Subscription).filter_by(customer_id=data.stripe_customer).first()
    )

    if not stripe_data:
        log(
            log.ERROR,
            f"create_subscription: customer {data.stripe_customer} doesn't exists",
        )
        raise HTTPException(status_code=404, detail="This user was not found")

    log(
        log.INFO,
        f"create_subscription: customer {data.stripe_customer} exists: {bool(stripe_data)}",
    )

    # insert data into the stripe_data model
    stripe_data.subscription_id = data.subscription_id
    db.add(stripe_data)
    db.commit()
    db.refresh(stripe_data)
    log(
        log.INFO,
        f"create_subscription: subscription_id {stripe_data.subscription_id} was inserted for\
        {stripe_data.customer_id} - {stripe_data.user}",
    )

    # create my response
    my_response = schema.StripeSubscription(
        email=stripe_data.user.email,
        stripe_customer=stripe_data.customer_id,
        subscription_id=stripe_data.subscription_id,
    )

    return my_response


@router.put("/update_subscription", status_code=204)
def update_subscription(data: schema.StripeSubscription, db: Session = Depends(get_db)):

    stripe_data_subscription = (
        db.query(model.Subscription)
        .filter_by(subscription_id=data.subscription_id)
        .first()
    )

    if not stripe_data_subscription:
        log(
            log.ERROR,
            f"update_subscription: subscription_id {data.subscription_id} doesn't exists",
        )
        raise HTTPException(status_code=404, detail="There is no such subscription_id")

    cancel_at_period_end = data.subscription["cancel_at_period_end"]
    cancel_at = data.subscription["cancel_at"]
    product_key = data.subscription["plan"]["id"]

    # stripe_data.subscription_id = data.subscription_id
    if product_key == BASIC_PRICE_LOOKUP_KEY:
        stripe_data_subscription.type = model.Subscription.SubscriptionType.Basic
        stripe_data_subscription.product_id = product_key
    if product_key == ADVANCE_PRICE_LOOKUP_KEY:
        stripe_data_subscription.type = model.Subscription.SubscriptionType.Advance
        stripe_data_subscription.product_id = product_key

    log(
        log.INFO,
        f"update_subscription: subscription_id {data.subscription_id} exists: {bool(stripe_data_subscription)}",
    )

    stripe_data_subscription.cancel_at_period_end = cancel_at_period_end
    stripe_data_subscription.cancel_at = datetime.now() if cancel_at else None
    db.add(stripe_data_subscription)
    db.commit()
    db.refresh(stripe_data_subscription)

    return Response(status_code=204)


@router.post("/delete_subscription", status_code=204)
def delete_subscription(data: schema.StripeSubscription, db: Session = Depends(get_db)):
    """
    This route deletes row with accepted subscription_id in the stripe_data model
    You can use it when user stop his type
    """
    # check existance of accepted subscription_id
    stripe_data = (
        db.query(model.Subscription)
        .filter_by(subscription_id=data.subscription_id)
        .first()
    )

    if not stripe_data:
        log(
            log.ERROR,
            f"delete_subscription: subscription_id {data.subscription_id} doesn't exists",
        )
        raise HTTPException(status_code=404, detail="There is no such subscription_id")

    log(
        log.INFO,
        f"delete_subscription: subscription_id {data.subscription_id} exists: {bool(stripe_data)}",
    )

    # delete data from stripe_data model
    stripe_data.session_id = ""
    stripe_data.cancel_at_period_end = True

    stripe_data.subscription_id = ""
    stripe_data.product_id = ""
    stripe_data.type = model.Subscription.SubscriptionType.Basic

    db.commit()
    # db.refresh(stripe_data)
    log(
        log.INFO,
        f"delete_subscription: row with subscription_id {data.subscription_id} was deleted",
    )

    return Response(status_code=204)
