from fastapi import HTTPException, Response, Depends, APIRouter
from typing import List
from app import model, oauth2, schema
from app.database import get_db
from sqlalchemy.orm import Session
from app.logger import log

router = APIRouter(prefix="/backend/survey", tags=["Surveys"])


@router.get("/", response_model=List[schema.Survey])
def get_surveys(db: Session = Depends(get_db)):
    surveys = db.query(model.Survey).all()
    log(log.INFO, "get_surveys: count surveys [%s]", len(surveys))
    return surveys


@router.post("/", status_code=201, response_model=schema.Survey)
def create_survey(
    survey: schema.SurveyCreate,
    db: Session = Depends(get_db),
    # current_user: int = Depends(oauth2.get_current_user),
):
    user = db.query(model.User).filter(model.User.id == survey.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this key not found")

    log(log.INFO, "create_survey: user [%s]", user)

    new_survey = model.Survey(
        title=survey.title,
        user_id=survey.user_id,
    )

    log(log.INFO, "create_survey: new_survey [%s]", new_survey)
    db.add(new_survey)
    db.commit()
    db.refresh(new_survey)

    return new_survey


@router.get("/{id}", response_model=schema.Survey)
def get_survey(id: int, db: Session = Depends(get_db)):
    survey = db.query(model.Survey).get(id)
    log(log.INFO, "get_survey: survey [%s]", survey)
    if not survey:
        raise HTTPException(status_code=404, detail="This survey was not found")
    return survey


@router.delete("/{id}", status_code=204)
def delete_survey(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    deleted_survey = db.query(model.Survey).filter_by(id=id)
    if not deleted_survey.first():
        raise HTTPException(status_code=404, detail="This survey was not found")

    if deleted_survey.first().user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    deleted_survey.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=204)


@router.put("/{id}", response_model=schema.Survey)
def update_survey(
    id: int,
    survey: schema.SurveyCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    updated_survey = db.query(model.Survey).filter_by(id=id)

    if not updated_survey.first():
        raise HTTPException(status_code=404, detail="This survey was not found")

    if updated_survey.first().user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")

    updated_survey.update(survey.dict(), synchronize_session=False)
    db.commit()

    return updated_survey.first()
