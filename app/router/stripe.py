from fastapi import Depends, APIRouter
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


# @router.post("/session")
# # TODO: /create_stripe_session, recieve email, customer_id, session_id, advance or base subscr; write session_id
# # response: all field of stripe model + email
# def create_stripe_session(
#     stripe_data: schema.StripeData, db: Session = Depends(get_db)
# ):

#     if not stripe_data.email:
#         log(log.INFO("Email not found"))
#         return "Email not found"

#     user = db.query(model.User).filter(model.User.email == stripe_data.email).first()

#     if not user:
#         user = model.User(email=stripe_data.email)
#         db.add(user)
#         db.commit()
#         db.refresh(user)

#     log(log.INFO, "get_user_surveys: user [%s]", user)

#     product_key = None
#     if stripe_data.advance_product_key:
#         stripe_model = model.Stripe(subscription=model.Stripe.SubscriptionType.Advance)
#     else:
#         stripe_model = model.Stripe(subscription=model.Stripe.SubscriptionType.Basic)

#     db.add(stripe_model)
#     db.commit()
#     db.refresh(stripe_model)

#     user.stripe_data_id = stripe_model.id
#     product_key = stripe_data.basic_product_key
#     db.commit()
#     db.refresh(user)

#     # success_url=
#     # cancel_url=
#     try:
#         # prices = stripe.Price.list(lookup_keys=[lookup_key], expand=["data.product"])
#         customer = stripe.Customer.create(
#             email=stripe_data.email,
#             description="My First Test Customer",
#         )
#         checkout_session = stripe.checkout.Session.create(
#             line_items=[
#                 {
#                     "price": product_key,
#                     "quantity": 1,
#                 },
#             ],
#             customer_email=stripe_data.email,
#             mode="subscription",
#             success_url=SERVER_HOST
#             + "/user_profile/user"
#             + "?success=true&session_id={CHECKOUT_SESSION_ID}",
#             cancel_url=SERVER_HOST + "/user_profile/user" + "?canceled=true",
#         )

#         stripe_model.stripe_customer_id = customer.stripe_id
#         stripe_model.stripe_session_id = checkout_session.stripe_id
#         db.commit()
#         db.refresh(stripe_model)

#         session_data = {
#             "stripe_session_id": checkout_session.stripe_id,
#             "checkout_session_url": checkout_session.url,
#         }

#         return session_data
#     except Exception as e:
#         print(e)
#         return "Server error", 500


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
