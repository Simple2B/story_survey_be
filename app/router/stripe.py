from fastapi import Depends, APIRouter, HTTPException
from app import model, schema
from app.database import get_db
from sqlalchemy.orm import Session
from app.config import settings
from app.logger import log

router = APIRouter(prefix="/backend/stripe", tags=["Stripe"])


@router.post("/create_customer", response_model=schema.UserOut)
def create_stripe_customer(data: schema.CreateCustomer, db: Session = Depends(get_db)):
    """
    This route insert cusromer_id in stripe_data model and return updated user's data.
    """

    # check existance of user with such email
    user = db.query(model.User).filter(model.User.email == data.email).first()

    if not user:
        user = model.User(email=data.email)
        db.add(user)
        db.commit()
        db.refresh(user)

    # check existance of such customer_id
    stripe_customer = (
        db.query(model.Stripe)
        .filter(model.Stripe.customer_id == data.stripe_customer)
        .first()
    )

    if not stripe_customer:
        stripe_customer = model.Stripe(customer_id=data.stripe_customer)
        stripe_customer.user_id = user.id
        db.add(stripe_customer)
        db.commit()
        db.refresh(stripe_customer)

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


# # TODO: /create_stripe_session, recieve email, customer_id, session_id, advance or base subscr; write session_id
# # response: all field of stripe model + email
@router.post("/create_stripe_session", response_model=schema.UserOut)
def create_stripe_session(data: schema.StripeData, db: Session = Depends(get_db)):
    # check existance of user
    user = db.query(model.User).filter_by(email=data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="This user was not found")

    # check existance of such customer_id in model stripe_data
    stripe_data = (
        db.query(model.Stripe).filter_by(customer_id=data.stripe_customer).first()
    )
    if not stripe_data:
        raise HTTPException(
            status_code=404, detail="You haven`t created stripe customer_id"
        )

    # insert data into the stripe_data model
    stripe_data.session_id = data.stripe_session_id
    if data.basic_product_key:
        stripe_data.subscription = model.Stripe.SubscriptionType.Basic
        stripe_data.product_id = data.basic_product_key
    else:
        stripe_data.subscription = model.Stripe.SubscriptionType.Advance
        stripe_data.product_id = data.advance_product_key
    db.commit()
    db.refresh(stripe_data)

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


# @router.post("/create_portal_session")
# TODO: /update_subscr
# def customer_portal(data: schema.StripePortal, db: Session = Depends(get_db)):
#     data
#     # checkout_session_id = request.form.get("session_id")
#     checkout_session = stripe.checkout.Session.retrieve(data.session_id)

#     # This is the URL to which the customer will be redirected after they are
#     # done managing their billing with the portal.
#     return_url = SERVER_HOST
#     customer_id = checkout_session.customer

#     portalSession = stripe.billing_portal.Session.create(
#         customer=customer_id,
#         return_url=return_url + "/user_profile/user",
#     )
#     return portalSession.url
