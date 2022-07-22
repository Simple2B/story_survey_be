import enum
from typing import List
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Union


from .survey import Survey


class User(BaseModel):
    class Config:
        orm_mode = True


class UserInfoSubscription(BaseModel):
    type: Optional[enum.Enum]
    customer_id: Optional[str]
    session_id: Optional[str]
    cancel_at: Optional[str]
    cancel_at_period_end: Optional[Union[bool, None]]
    subscription_id: Optional[str]
    product_id: Optional[str]


class UserOut(User):
    id: int
    uuid: Optional[str]
    username: Optional[str]
    email: str
    created_at: datetime
    role: Optional[enum.Enum]
    image: Optional[str]

    subscription_info: Optional[UserInfoSubscription]

    # type: Optional[enum.Enum]
    # customer_id: Optional[str]
    # session_id: Optional[str]
    # cancel_at: Optional[datetime]
    # cancel_at_period_end: Optional[Union[bool, None]]
    # subscription_id: Optional[str]
    # product_id: Optional[str]

    surveys: Optional[List[Survey]]


class AllUsers(BaseModel):
    data: list
    data_length: int
