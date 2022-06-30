from typing import Optional
from pydantic import BaseModel


class Stripe(BaseModel):
    orm_mode = True


class CreateCustomer(Stripe):
    stripe_customer: str


class StripeData(Stripe):
    email: str
    basic_product_key: Optional[str]
    advance_product_key: Optional[str]


class StripePortal(Stripe):
    session_id: str
