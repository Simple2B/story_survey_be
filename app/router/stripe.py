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

    if not user:
        user = model.User(email=data.email)
        db.add(user)
        db.commit()
        db.refresh(user)
        log(
            log.INFO, f"create_stripe_customer: user {data.email} created: {bool(user)}"
        )
    log(log.INFO, "create_stripe_customer: user [%s] found", data.email)

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
            "create_stripe_customer: customer [%s] created ",
            data.stripe_customer,
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

    # check existance of such customer_id
    stripe_customer = db.query(model.Subscription).filter(
        model.Subscription.customer_id == data.customer_id
    )

    if not stripe_customer.first():
        log(log.ERROR, "delete_customer: customer doesn't exists")
        Response(status_code=404)

    log(log.INFO, "delete_customer: customer [%s] exists", data.customer_id)

    stripe_customer.delete()
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

    if not user:
        log(log.ERROR, "create_stripe_session: user [%s] doesn't exists", data.email)
        raise HTTPException(status_code=404, detail="This user was not found")

    log(log.INFO, "create_stripe_session: user [%s] exists", data.email)

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
        log(log.INFO, "create_stripe_session: customer_id [%s]", data.stripe_customer)

    log(
        log.INFO, "create_stripe_session: customer_id [%s] exists", data.stripe_customer
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
        "create_stripe_session: data was inserted: session id [%s], product id [%s]",
        stripe_data.session_id,
        stripe_data.product_id,
    )
    log(log.INFO, "create_stripe_session: for user [%s]", {stripe_data.user})

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
            "create_subscription: customer [%] doesn't exists",
            data.stripe_customer,
        )
        raise HTTPException(status_code=404, detail="This user was not found")

    log(log.INFO, "create_subscription: customer [%s] exists ", data.stripe_customer)

    # insert data into the stripe_data model
    stripe_data.subscription_id = data.subscription_id
    db.add(stripe_data)
    db.commit()
    db.refresh(stripe_data)
    log(
        log.INFO,
        "create_subscription: subscription_id [%s] was inserted for stripe customer [%s]",
        stripe_data.subscription_id,
        stripe_data.customer_id,
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
            "update_subscription: subscription_id [%s] doesn't exists",
            data.subscription_id,
        )
        raise HTTPException(status_code=404, detail="There is no such subscription_id")

    log(
        log.ERROR,
        "update_subscription: subscription_id [%s] exists",
        data.subscription_id,
    )

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

    stripe_data_subscription.cancel_at_period_end = cancel_at_period_end
    stripe_data_subscription.cancel_at = datetime.now() if cancel_at else None
    db.commit()
    db.refresh(stripe_data_subscription)

    log(
        log.ERROR,
        "update_subscription: subscription type [%s]",
        stripe_data_subscription.type,
    )

    return Response(status_code=204)


@router.post("/delete_subscription", status_code=204)
def delete_subscription(data: schema.DeleteSubscription, db: Session = Depends(get_db)):
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
            "delete_subscription: subscription_id [%s] doesn't exists",
            data.subscription_id,
        )
        raise HTTPException(status_code=404, detail="There is no such subscription_id")

    log(
        log.INFO,
        "delete_subscription: subscription_id [%s] exists",
        data.subscription_id,
    )

    # delete data from stripe_data model
    stripe_data.session_id = ""
    stripe_data.cancel_at_period_end = True

    stripe_data.subscription_id = ""
    stripe_data.product_id = ""
    stripe_data.type = model.Subscription.SubscriptionType.Basic

    db.commit()
    log(
        log.INFO,
        "delete_subscription: row with subscription_id [%s] was deleted",
        data.subscription_id,
    )

    return Response(status_code=204)
