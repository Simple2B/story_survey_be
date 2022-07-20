from typing import Optional
from pydantic import BaseModel


class Subscription(BaseModel):
    class Config:
        orm_mode = True


class CreateOrDeleteCustomer(Subscription):
    email: str
    stripe_customer: str


class StripeSession(Subscription):
    session: Optional[dict]
    email: str
    stripe_customer: str
    product_key: Optional[str]
    stripe_session_id: str


class StripeSubscription(Subscription):
    email: Optional[str]
    stripe_customer: Optional[str]
    status: Optional[str]
    subscription: Optional[dict]
    subscription_id: Optional[str]
    cancel_at_period_end: Optional[bool]
    subscription_id: str


class DeleteSubscription(Subscription):
    subscription_id: str


class StripeCustomer(Subscription):
    customer_id: str


class StripePortal(Subscription):
    session_id: str


# class StripeSubscriptionUpdate(Subscription):
#     email: Optional[str]
#     stripe_customer: Optional[str]
#     subscription_id: str
