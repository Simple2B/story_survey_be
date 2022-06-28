from uuid import uuid4
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship

from app.database import Base


# class StripeHistory(Base):
#     __tablename__ = "stripe_history"

#     id = Column(Integer, primary_key=True)

#     product_id = Column(
#         String(),
#     )
#     user_id = Column(Integer, ForeignKey("users.id"))
#     user = relationship("User")

#     def __repr__(self) -> str:
#         return f"<{self.id}: {self.title} at {self.created_at}>"
