from typing import Optional
from pydantic import BaseModel


class Stripe(BaseModel):
    orm_mode = True


class CreateCustomer(Stripe):
    email: str
    stripe_customer: str


class StripeData(Stripe):
    email: str
    basic_product_key: Optional[str]
    advance_product_key: Optional[str]
    stripe_customer: str
    stripe_session_id: str


class StripePortal(Stripe):
    session_id: str
