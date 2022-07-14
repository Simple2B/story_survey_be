from typing import Optional
from pydantic import BaseModel


class Stripe(BaseModel):
    class Config:
        orm_mode = True


class CreateOrDeleteCustomer(Stripe):
    email: str
    stripe_customer: str


class StripeData(Stripe):
    email: str
    basic_product_key: Optional[str]
    advance_product_key: Optional[str]
    stripe_customer: str
    stripe_session_id: str
    subscription_id: Optional[str]


class StripeSubscription(Stripe):
    email: Optional[str]
    stripe_customer: Optional[str]
    status: Optional[str]
    subscription: Optional[dict]
    subscription_id: Optional[str]
    cancel_at_period_end: Optional[bool]
    subscription_id: str


class StripePortal(Stripe):
    session_id: str


# class StripeSubscriptionUpdate(Stripe):
#     email: Optional[str]
#     stripe_customer: Optional[str]
#     subscription_id: str
