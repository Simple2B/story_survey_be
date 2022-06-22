from fastapi import HTTPException, Response, Depends, APIRouter
from typing import List
from app import model, oauth2, schema
from app.database import get_db
from sqlalchemy.orm import Session
from app.logger import log

router = APIRouter(prefix="/backend/survey", tags=["Surveys"])


@router.get("/surveys", response_model=List[schema.Survey])
def get_surveys(db: Session = Depends(get_db)):
    surveys = db.query(model.Survey).all()
    log(log.INFO, "get_surveys: count surveys [%s]", len(surveys))

    surveys_with_question = []
    if not surveys:
        log(log.INFO, "get_surveys: surveys count [%d]", len(surveys))
        return surveys_with_question

    for survey in surveys:
        questions = (
            db.query(model.Question).filter(model.Question.survey_id == survey.id).all()
        )

        surveys_with_question.append(
            {
                "id": survey.id,
                "title": survey.title,
                "created_at": survey.created_at,
                "user_id": survey.user_id,
                "email": survey.user.email,
                "questions": questions,
            }
        )

    return surveys_with_question


@router.get("/{email}", response_model=List[schema.Survey])
def get_user_surveys(email: str, db: Session = Depends(get_db)):
    user = db.query(model.User).filter(model.User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User with this key not found")

    log(log.INFO, "get_user_surveys: user [%s]", user)

    surveys = db.query(model.Survey).filter(model.Survey.user_id == user.id).all()

    log(log.INFO, "get_survey: surveys count [%d]", len(surveys))

    surveys_with_question = []
    if not surveys:
        log(log.INFO, "get_survey: surveys count [%d]", len(surveys))
        return surveys_with_question

    for survey in surveys:
        questions = (
            db.query(model.Question).filter(model.Question.survey_id == survey.id).all()
        )

        surveys_with_question.append(
            {
                "id": survey.id,
                "title": survey.title,
                "created_at": survey.created_at,
                "user_id": survey.user_id,
                "email": user.email,
                "questions": [item.question for item in questions],
            }
        )

    return surveys_with_question


@router.post("/create_survey", status_code=201, response_model=schema.Survey)
def create_survey(
    survey: schema.SurveyCreate,
    db: Session = Depends(get_db),
    # current_user: int = Depends(oauth2.get_current_user),
):
    user = db.query(model.User).filter(model.User.email == survey.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with this key not found")

    log(log.INFO, "create_survey: user [%s]", user)

    new_survey: model.Survey = model.Survey(
        title=survey.title,
        user_id=user.id,
    )
    db.add(new_survey)
    db.commit()
    db.refresh(new_survey)
    log(log.INFO, "create_survey: new_survey [%s]", new_survey)

    if survey.questions and len(survey.questions) > 0:
        survey_id = new_survey.id
        log(log.INFO, "create_survey: count of questions [%d]", len(survey.questions))
        for question in survey.questions:
            create_question = model.Question(
                question=question,
                survey_id=survey_id,
            )
            db.add(create_question)
            db.commit()
            db.refresh(create_question)

        log(log.INFO, "create_survey: questions [%d] created", len(survey.questions))

    return new_survey


@router.get("/{id}", response_model=schema.Survey)
def get_survey(id: int, db: Session = Depends(get_db)):
    survey = db.query(model.Survey).get(id)
    log(log.INFO, "get_survey: survey [%s]", survey)
    if not survey:
        raise HTTPException(status_code=404, detail="This survey was not found")
    return survey


@router.post("/delete_survey", status_code=204)
def delete_survey(
    data: schema.SurveyDelete,
    db: Session = Depends(get_db),
    # current_user: int = Depends(oauth2.get_current_user),
):
    user = db.query(model.User).filter(model.User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User with this key not found")

    log(log.INFO, "delete_survey: user [%s]", user)

    user_surveys = (
        db.query(model.Survey).filter((model.Survey.user_id == user.id)).all()
    )

    if len(user_surveys) > 0:
        for survey in user_surveys:
            if data.survey_id == survey.id:
                del_survey = (
                    db.query(model.Survey)
                    .filter((model.Survey.id == int(survey.id)))
                    .first()
                )
                log(log.INFO, "delete_survey: delete survey [%s]", survey)

                questions = db.query(model.Question).filter(
                    (model.Question.survey_id == del_survey.id)
                )

                questions.delete(synchronize_session=False)
                db.commit()
                # db.refresh()
                log(log.INFO, "delete_survey:  questions deleted")

                del_survey = db.query(model.Survey).filter(
                    (model.Survey.id == int(survey.id))
                )

                del_survey.delete(synchronize_session=False)
                db.commit()
                log(log.INFO, "delete_survey:  survey deleted")

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
