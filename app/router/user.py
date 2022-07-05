from fastapi import HTTPException, Depends, APIRouter
from typing import List
from app import model, schema
from app.database import get_db
from sqlalchemy.orm import Session
from app.logger import log

router = APIRouter(prefix="/backend/user", tags=["Users"])


@router.get("/get_users", response_model=List[schema.UserOut])
def get_users(db: Session = Depends(get_db)):

    users = db.query(model.User).all()
    log(log.INFO, f"get_users: number of users {len(users)}")
    if len(users) > 0:

        return [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at,
                "role": user.role,
                "image": user.image,
                "surveys": [
                    get_survey_info(survey) for survey in get_surveys_for_user(user, db)
                ]
                if len(get_surveys_for_user(user, db)) > 0
                else [],
            }
            for user in users
        ]

    return users


@router.post("/create_user", status_code=201, response_model=schema.UserOut)
def create_user(n_user: schema.UserCreate, db: Session = Depends(get_db)):

    user = db.query(model.User).filter(model.User.email == n_user.email).first()
    log(log.INFO, f"create_user: user {n_user.email} exists: {bool(user)}")

    if not user:
        user = model.User(**n_user.dict())
        db.add(user)
        db.commit()
        db.refresh(user)

    log(log.INFO, f"create_user: user {user}")
    return user


@router.get("/id/{id}", response_model=schema.UserOut)
def get_user_by_id(
    id: int,
    db: Session = Depends(get_db),
):
    user = db.query(model.User).get(int(id))

    if not user:
        raise HTTPException(status_code=404, detail="This user was not found")

    stripe_info = db.query(model.Stripe).filter(model.Stripe.user_id == user.id).first()

    if not stripe_info:
        return get_info_user(user, db)

    return get_user_with_stripe_info(user, stripe_info, db)


@router.get("/email/{email}", response_model=schema.UserOut)
def get_user(
    email: str,
    db: Session = Depends(get_db),
):
    user = db.query(model.User).filter(model.User.email == email).first()
    log(log.INFO, f"get_user: user {email} exists: {bool(user)}")

    if not user:
        log(log.ERROR, f"get_user: no user {email}")
        raise HTTPException(status_code=404, detail="This user was not found")

    stripe_info = db.query(model.Stripe).filter(model.Stripe.user_id == user.id).first()
    log(log.INFO, f"get_user: stripe info exists: {bool(stripe_info)}")

    if not stripe_info:
        return get_info_user(user, db)

    return get_user_with_stripe_info(user, stripe_info, db)


# helper functions


def get_surveys_for_user(user, db):
    return db.query(model.Survey).filter(model.Survey.user_id == user.id).all()


def get_survey_info(survey: schema.Survey):
    questions = []
    for q in survey.questions:
        if len(q.question) > 0:
            questions.append(q)
    return {
        "id": survey.id,
        "uuid": survey.uuid,
        "title": survey.title,
        "description": survey.description,
        "created_at": survey.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
        "user_id": survey.user_id,
        "questions": questions,
    }


def get_info_user(user, db):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at,
        "role": user.role,
        "image": user.image,
        "surveys": [
            get_survey_info(survey) for survey in get_surveys_for_user(user, db)
        ]
        if len(get_surveys_for_user(user, db)) > 0
        else [],
    }


def get_user_with_stripe_info(user, stripe_info, db):
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at,
        "role": user.role,
        "image": user.image,
        "customer_id": stripe_info.customer_id,
        "session_id": stripe_info.session_id,
        "subscription": stripe_info.subscription,
        "subscription_id": stripe_info.subscription_id,
        "product_id": stripe_info.product_id,
        "surveys": [
            get_survey_info(survey) for survey in get_surveys_for_user(user, db)
        ]
        if len(get_surveys_for_user(user, db)) > 0
        else [],
    }
