from fastapi import HTTPException, Depends, APIRouter
from app import model, schema, oauth2
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/backend/user", tags=["Users"])


@router.post("/create_user", status_code=201, response_model=schema.UserOut)
def create_user(n_user: schema.UserCreate, db: Session = Depends(get_db)):

    user = db.query(model.User).filter(model.User.email == n_user.email).first()

    if not user:
        # if n_user.provider:
        #     user = model.User(
        #         username=n_user.username,
        #         email=n_user.email,
        #         image=n_user.image,
        #     )
        #     db.add(user)
        #     db.commit()
        #     db.refresh(user)
        #     return user

        user = model.User(**n_user.dict())
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


@router.get("/{id}", response_model=schema.UserOut)
def get_user(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    user = db.query(model.User).get(id)

    if not user:
        raise HTTPException(status_code=404, detail="This user was not found")

    return user
