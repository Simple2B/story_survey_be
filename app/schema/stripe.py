from pydantic import BaseModel


class Stripe(BaseModel):
    orm_mode = True


class StripeData(Stripe):
    email: str
    key: str


class StripePortal(Stripe):
    session_id: str
