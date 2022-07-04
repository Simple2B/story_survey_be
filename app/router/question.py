from cmath import log
from fastapi import HTTPException, Response, Depends, APIRouter
from typing import List
from app import model, oauth2, schema
from app.database import get_db
from sqlalchemy.orm import Session
from app.logger import log

router = APIRouter(prefix="/backend/question", tags=["Questions"])


@router.get("/", response_model=List[schema.Question])
def get_questions(db: Session = Depends(get_db)):
    questions = db.query(model.Question).all()
    log(log.INFO, f"get_questions: {len(questions)} exist")
    return questions


@router.post("/", status_code=201, response_model=schema.Question)
def create_question(
    question_info: schema.QuestionCreate,
    db: Session = Depends(get_db),
    # current_user: int = Depends(oauth2.get_current_user),
):
    new_question = model.Question(
        question=question_info.question,
        survey_id=question_info.survey_id,
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    log(
        log.INFO,
        f"create_question: question '{new_question.question}' created for survey {new_question.survey}",
    )

    return new_question


@router.get("/{id}", response_model=schema.Question)
def get_question(id: int, db: Session = Depends(get_db)):
    question = db.query(model.Question).get(id)
    log(log.INFO, f"get_question: question {id} exists: {bool(question)}")

    if not question:
        log(log.ERROR, f"get_question: question {id} doesn't exist")
        raise HTTPException(
            status_code=404, detail="get_question: This question was not found"
        )
    return question


@router.delete("/{id}", status_code=204)
def delete_question(
    id: int,
    db: Session = Depends(get_db),
    # current_user: int = Depends(oauth2.get_current_user),
):
    deleted_question = db.query(model.Question).filter_by(id=id).first()
    log(log.INFO, f"delete_question: question {id} exists: {bool(deleted_question)}")

    if not deleted_question:
        log(log.ERROR, f"delete_question: question {id} doesn't exists")
        raise HTTPException(
            status_code=404, detail="delete_question: This question was not found"
        )

    # if deleted_question.first().user_id != current_user.id:
    #     log(log.ERROR, f"delete_question: current user id {current_user.id} doesn't match question user_id {deleted_question.first().user_id}")
    #     raise HTTPException(
    #         status_code=403, detail="delete_question: Not enough permissions"
    #     )

    db.delete(deleted_question)
    db.commit()
    log(log.INFO, f"delete_question: question {id} was deleted")

    return Response(status_code=204)


@router.put("/{id}", response_model=schema.Question)
def update_question(
    id: int,
    question_info: schema.QuestionCreate,
    db: Session = Depends(get_db),
    # current_user: int = Depends(oauth2.get_current_user),
):
    update_question = db.query(model.Question).filter_by(id=id).first()
    log(log.INFO, f"update_question: question {id} exists: {bool(update_question)}")

    if not update_question:
        log(log.ERROR, f"delete_question: question {id} doesn't exists")
        raise HTTPException(
            status_code=404, detail="update_question: This question was not found"
        )

    # if update_question.first().user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=403, detail="update_question: Not enough permissions"
    #     )

    for key, val in question_info.dict().items():
        setattr(update_question, key, val)
    # update_question.update(question_info.dict(), synchronize_session=False)
    db.commit()
    db.refresh(update_question)
    log(log.INFO, f"update_question: question {id} was updated")

    return update_question
