from typing import Optional
from pydantic import BaseModel


class Subscription(BaseModel):
    class Config:
        orm_mode = True


class CreateOrDeleteCustomer(Subscription):
    email: str
    stripe_customer: str


class StripeData(Subscription):
    session: Optional[dict]
    email: str
    basic_product_key: Optional[str]
    advance_product_key: Optional[str]
    stripe_customer: str
    stripe_session_id: str
    subscription_id: Optional[str]


class StripeSubscription(Subscription):
    email: Optional[str]
    stripe_customer: Optional[str]
    status: Optional[str]
    subscription: Optional[dict]
    subscription_id: Optional[str]
    cancel_at_period_end: Optional[bool]
    subscription_id: str


class StripePortal(Subscription):
    session_id: str


# class StripeSubscriptionUpdate(Subscription):
#     email: Optional[str]
#     stripe_customer: Optional[str]
#     subscription_id: str
