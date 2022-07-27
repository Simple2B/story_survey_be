from fastapi import HTTPException, Response, Depends, APIRouter
from typing import List
from app import model, schema
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
        "create_question: question [%s] created for survey [%s]",
        new_question.question,
        new_question.survey,
    )

    return new_question


@router.get("/{id}", response_model=schema.Question)
def get_question(id: int, db: Session = Depends(get_db)):
    question = db.query(model.Question).get(id)

    if not question:
        log(log.ERROR, "get_question: question [%d] doesn't exist", id)
        raise HTTPException(
            status_code=404, detail="get_question: This question was not found"
        )
    log(log.INFO, "get_question: question [%d] exists", id)
    return question


@router.delete("/{id}", status_code=204)
def delete_question(
    id: int,
    db: Session = Depends(get_db),
    # current_user: int = Depends(oauth2.get_current_user),
):
    deleted_question = db.query(model.Question).filter_by(id=id).first()

    if not deleted_question:
        log(log.INFO, f"delete_question: question doesn't exists")
        raise HTTPException(
            status_code=404, detail="delete_question: This question was not found"
        )

    answers = db.query(model.Answer).filter(model.Answer.question_id == id)

    if answers.all():
        log(log.INFO, "delete_question: count [%d] of answers: ", len(answers.all()))
        answers.delete()
        db.commit()
        log(log.INFO, "delete_question:  answers deleted")

    # if deleted_question.first().user_id != current_user.id:
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

    if not update_question:
        log(log.ERROR, "delete_question: question doesn't exists")
        raise HTTPException(
            status_code=404, detail="update_question: This question was not found"
        )

    log(log.INFO, "update_question: question [%s] exists", update_question)

    # if update_question.first().user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=403, detail="update_question: Not enough permissions"
    #     )

    for key, val in question_info.dict().items():
        setattr(update_question, key, val)
    # update_question.update(question_info.dict(), synchronize_session=False)
    db.commit()
    db.refresh(update_question)
    log(log.INFO, "update_question: question [%d] was updated", id)

    return update_question
