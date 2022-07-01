from fastapi import HTTPException, Depends, APIRouter
from app import model, schema
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/backend/user", tags=["Users"])


@router.post("/create_user", status_code=201, response_model=schema.UserOut)
def create_user(n_user: schema.UserCreate, db: Session = Depends(get_db)):

    user = db.query(model.User).filter(model.User.email == n_user.email).first()

    if not user:
        user = model.User(**n_user.dict())
        db.add(user)
        db.commit()
        db.refresh(user)

    return user


@router.get("/{email}", response_model=schema.UserOut)
def get_user(email: str, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="This user was not found")

    return user
