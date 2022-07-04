from fastapi import Depends, APIRouter
from app import model, schema
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/backend/history", tags=["History"])


@router.get("/", status_code=201, response_model=schema.History)
def get_history(db: Session = Depends(get_db)):

    all_users = db.query(model.User).all()
    my_response = schema.History(users=all_users)

    return my_response


# TODO: route for recieving information aboute all users
# /backend/history/users, just request
# pagination
# username, email, surveys (titles), questions
# All from tables User, Stripe, survey, question, all answers with session_id