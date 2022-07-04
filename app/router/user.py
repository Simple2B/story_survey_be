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


@router.get("/{email}", response_model=schema.UserOut)
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
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "created_at": user.created_at,
            "role": user.role,
            "image": user.image,
        }

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
    }
