from fastapi import Depends, APIRouter, HTTPException, Response
from app import model, schema
from app.database import get_db
from sqlalchemy.orm import Session
from app.logger import log


router = APIRouter(prefix="/backend/stripe", tags=["Stripe"])


# @router.post("/create_customer", response_model=schema.UserOut)
# def create_stripe_customer(
#     data: schema.CreateOrDeleteCustomer, db: Session = Depends(get_db)
# ):
#     """
#     This route insert customer_id in stripe_data model and return updated user's data.
#     You should use this route when you create customer on Stripe platform and have to save his customer_id.
#     """

#     # check existance of user with such email
#     user = db.query(model.User).filter(model.User.email == data.email).first()
#     log(log.INFO, f"create_stripe_customer: user {data.email} exists: {bool(user)}")

#     if not user:
#         user = model.User(email=data.email)
#         db.add(user)
#         db.commit()
#         db.refresh(user)
#         log(
#             log.INFO, f"create_stripe_customer: user {data.email} created: {bool(user)}"
#         )

#     # check existance of such customer_id
#     stripe_customer = (
#         db.query(model.Stripe)
#         .filter(model.Stripe.customer_id == data.stripe_customer)
#         .first()
#     )

#     if not stripe_customer:
#         stripe_customer = model.Stripe(customer_id=data.stripe_customer)
#         stripe_customer.user_id = user.id
#         db.add(stripe_customer)
#         db.commit()
#         db.refresh(stripe_customer)
#         log(
#             log.INFO,
#             f"create_stripe_customer: customer {data.stripe_customer} created: {bool(stripe_customer)}",
#         )
#         log(log.INFO, f"create_stripe_customer: for user {stripe_customer.user}")

#     log(
#         log.INFO,
#         f"create_stripe_customer: customer {data.stripe_customer} exists: {bool(stripe_customer)}",
#     )

#     # return users data
#     user_customer = schema.UserOut(
#         id=user.id,
#         username=user.username,
#         email=user.email,
#         created_at=user.created_at,
#         role=user.role,
#         image=user.image,
#         customer_id=stripe_customer.customer_id,
#     )
#     return user_customer


@router.delete("/delete_customer", status_code=204)
def delete_stripe_customer(
    data: schema.CreateOrDeleteCustomer, db: Session = Depends(get_db)
):
    """
    This route deletes data in stripe_data model if row with accepted customer_id has no session_id.
    You can use it if user pressed "Cancel button" on Stripe subscription page.
    """
    # check existance of such customer_id
    stripe_customer = (
        db.query(model.Stripe)
        .filter(model.Stripe.customer_id == data.stripe_customer)
        .first()
    )

    if not stripe_customer:
        log(
            log.ERROR,
            f"delete_customer: customer {data.stripe_customer} doesn't exists",
        )
        raise HTTPException(status_code=404, detail="There is no such customer_id")

    log(
        log.INFO,
        f"delete_customer: customer {data.stripe_customer} exists: {bool(stripe_customer)}",
    )

    # delete customer if he doesn't have session_id
    if stripe_customer.session_id:
        log(
            log.ERROR,
            f"delete_customer: customer {data.stripe_customer} has session_id",
        )
        raise HTTPException(status_code=400, detail="This customer has session_id")

    db.delete(stripe_customer)
    db.commit()
    log(log.INFO, f"delete_customer: customer {data.stripe_customer} was deleted")
    return Response(status_code=204)


@router.post("/create_stripe_session", response_model=schema.UserOut)
def create_stripe_session(data: schema.StripeData, db: Session = Depends(get_db)):
    """
    This route inserts stripe data (session_d, subscription, product_id) into the stripe_data model
    You can use it when user creates stripe checkout session
    """

    # check existance of user
    user = db.query(model.User).filter_by(email=data.email).first()
    log(log.INFO, f"create_stripe_session: user {data.email} exists: {bool(user)}")

    if not user:
        user = model.User(email=data.email)
        db.add(user)
        db.commit()
        db.refresh(user)
        log(
            log.INFO, f"create_stripe_customer: user {data.email} created: {bool(user)}"
        )

    # check existance of such customer_id
    stripe_data = (
        db.query(model.Stripe)
        .filter(model.Stripe.customer_id == data.stripe_customer)
        .first()
    )

    if not stripe_data:
        stripe_data = model.Stripe(customer_id=data.stripe_customer)
        stripe_data.user_id = user.id
        db.add(stripe_data)
        db.commit()
        db.refresh(stripe_data)
        log(
            log.INFO,
            f"create_stripe_customer: customer {data.stripe_customer} created: {bool(stripe_data)}",
        )
        log(log.INFO, f"create_stripe_customer: for user {stripe_data.user}")

    log(
        log.INFO,
        f"create_stripe_customer: customer {data.stripe_customer} exists: {bool(stripe_data)}",
    )

    # insert data into the stripe_data model
    stripe_data.session_id = data.stripe_session_id
    # stripe_data.subscription_id = data.subscription_id
    if data.basic_product_key:
        stripe_data.subscription = model.Stripe.SubscriptionType.Basic
        stripe_data.product_id = data.basic_product_key
    else:
        stripe_data.subscription = model.Stripe.SubscriptionType.Advance
        stripe_data.product_id = data.advance_product_key
    db.commit()
    db.refresh(stripe_data)
    log(
        log.INFO,
        f"create_stripe_session: data was inserted:\
            {stripe_data.session_id}, {stripe_data.subscription}, {stripe_data.product_id}",
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
        subscription=stripe_data.subscription,
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
        db.query(model.Stripe).filter_by(customer_id=data.stripe_customer).first()
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


@router.post("/delete_subscription", status_code=204)
def delete_subscription(data: schema.StripeSubscription, db: Session = Depends(get_db)):
    """
    This route deletes row with accepted subscription_id in the stripe_data model
    You can use it when user stop his subscription
    """
    # check existance of accepted subscription_id
    stripe_data = (
        db.query(model.Stripe).filter_by(subscription_id=data.subscription_id).first()
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
    db.delete(stripe_data)
    db.commit()
    log(
        log.INFO,
        f"delete_subscription: row with subscription_id {data.subscription_id} was deleted",
    )

    return Response(status_code=204)


@router.put("/update_subscription", status_code=204)
def update_subscription(data: schema.StripeSubscription, db: Session = Depends(get_db)):
    cancel_at_period_end = data.subscription["cancel_at_period_end"]

    stripe_data_subscription = (
        db.query(model.Stripe).filter_by(subscription_id=data.subscription_id).first()
    )

    if not stripe_data_subscription:
        log(
            log.ERROR,
            f"update_subscription: subscription_id {data.subscription_id} doesn't exists",
        )
        raise HTTPException(status_code=404, detail="There is no such subscription_id")

    log(
        log.INFO,
        f"update_subscription: subscription_id {data.subscription_id} exists: {bool(stripe_data_subscription)}",
    )

    stripe_data_subscription.cancel_at_period_end = cancel_at_period_end
    db.add(stripe_data_subscription)
    db.commit()
    db.refresh(stripe_data_subscription)

    return Response(status_code=204)
