import stripe
from fastapi import Depends, APIRouter
from app import model, schema
from app.database import get_db
from sqlalchemy.orm import Session
from app.config import settings
from app.logger import log

router = APIRouter(prefix="/backend/stripe", tags=["Stripe"])

# settings.STRIPE_PUBLIC_KEY
# settings.STRIPE_SECRET_KEY

stripe.api_key = settings.STRIPE_SECRET_KEY
SERVER_HOST = "http://localhost:3000"
# http://localhost:3000/user_profile/user


@router.post("/get_key")
def get_stripe_key():
    data = {
        "s_stripe": settings.STRIPE_SECRET_KEY,
        "BASIC_PRICE_LOOKUP_KEY": settings.BASIC_PRICE_LOOKUP_KEY,
        "ADVANCE_PRICE_LOOKUP_KEY": settings.ADVANCE_PRICE_LOOKUP_KEY,
    }
    return data


@router.post("/session")
def create_stripe_session(
    stripe_data: schema.StripeData, db: Session = Depends(get_db)
):

    if not stripe_data.email:
        log(log.INFO("Email not found"))
        return "Email not found"

    user = db.query(model.User).filter(model.User.email == stripe_data.email).first()

    if not user:
        user = model.User(email=stripe_data.email)
        db.add(user)
        db.commit()
        db.refresh(user)

    log(log.INFO, "get_user_surveys: user [%s]", user)

    product_key = None
    if stripe_data.advance_product_key:
        stripe_model = model.Stripe(subscription=model.Stripe.SubscriptionType.Advance)
    else:
        stripe_model = model.Stripe(subscription=model.Stripe.SubscriptionType.Basic)

    db.add(stripe_model)
    db.commit()
    db.refresh(stripe_model)

    user.stripe_data_id = stripe_model.id
    product_key = stripe_data.basic_product_key
    db.commit()
    db.refresh(user)

    # success_url=
    # cancel_url=
    try:
        # prices = stripe.Price.list(lookup_keys=[lookup_key], expand=["data.product"])
        customer = stripe.Customer.create(
            email=stripe_data.email,
            description="My First Test Customer",
        )
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    "price": product_key,
                    "quantity": 1,
                },
            ],
            customer_email=stripe_data.email,
            mode="subscription",
            success_url=SERVER_HOST
            + "/user_profile/user"
            + "?success=true&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=SERVER_HOST + "/user_profile/user" + "?canceled=true",
        )

        stripe_model.stripe_customer_id = customer.stripe_id
        stripe_model.stripe_session_id = checkout_session.stripe_id
        db.commit()
        db.refresh(stripe_model)

        session_data = {
            "stripe_session_id": checkout_session.stripe_id,
            "checkout_session_url": checkout_session.url,
        }

        return session_data
    except Exception as e:
        print(e)
        return "Server error", 500


@router.get("/stripe_session/{email}")
def get_stripe_session(email: str, db: Session = Depends(get_db)):
    email


@router.post("/create_portal_session")
def customer_portal(data: schema.StripePortal, db: Session = Depends(get_db)):
    data
    # For demonstration purposes, we're using the Checkout session to retrieve the customer ID.
    # Typically this is stored alongside the authenticated user in your database.
    # checkout_session_id = request.form.get("session_id")
    checkout_session = stripe.checkout.Session.retrieve(data.session_id)

    # This is the URL to which the customer will be redirected after they are
    # done managing their billing with the portal.
    return_url = SERVER_HOST
    customer_id = checkout_session.customer

    portalSession = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=return_url + "/user_profile/user",
    )
    return portalSession.url
