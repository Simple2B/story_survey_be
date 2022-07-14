import enum
from typing import List
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Union


from .survey import Survey


class UserOut(BaseModel):
    id: int
    uuid: Optional[str]
    username: Optional[str]
    email: str
    created_at: datetime
    role: Optional[enum.Enum]
    image: Optional[str]

    customer_id: Optional[str]
    session_id: Optional[str]
    subscription: Optional[enum.Enum]
    cancel_at_period_end: Optional[Union[bool, None]]
    subscription_id: Optional[str]
    product_id: Optional[str]

    surveys: Optional[List[Survey]]

    class Config:
        orm_mode = True
