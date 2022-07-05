from datetime import datetime
from fastapi import HTTPException, Response, Depends, APIRouter
from typing import List
from app import model, schema
from app.database import get_db
from sqlalchemy.orm import Session
from app.logger import log

router = APIRouter(prefix="/backend/answer", tags=["Answers"])


@router.get("/", response_model=List[schema.Answer])
def get_answers(db: Session = Depends(get_db)):
    answers = db.query(model.Answer).all()
    log(log.INFO, f"get_answers: [{len(answers)}] answers exist")
    return answers


@router.post("/create_answer", status_code=201, response_model=List[schema.Answer])
def create_answer(
    answer_info: List[schema.AnswerCreate],
    db: Session = Depends(get_db),
):
    answers = []
    sessions = []
    for item in answer_info:
        if len(item.session_id) > 0 and len(item.answer) > 0:
            start_time = datetime.strptime(item.start_time, "%m/%d/%Y, %H:%M:%S")
            create_session_next = model.SessionNext(
                timestamp_session_start=start_time,
                # timestamp_session_end=item.end_time,
                session=item.session_id,
            )
            db.add(create_session_next)
            db.commit()
            db.refresh(create_session_next)
            sessions.append(create_session_next)
            new_answer = model.Answer(
                answer=item.answer,
                question_id=item.question.id,
                session_id=create_session_next.id,
            )
            db.add(new_answer)
            db.commit()
            db.refresh(new_answer)
            answers.append(new_answer)

    log(log.INFO, f"create_answer: [{len(answers)} answers were created]")
    log(log.INFO, f"create_answer: [{len(sessions)} sessions were created]")

    if len(answers) > 0:
        answers = [
            {
                "id": answer.id,
                "answer": answer.answer,
                "survey_id": answer.question.survey_id,
                "created_at": answer.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                "session_id": answer.session_id,
                # "session": ,
                # "start_time": ,
                # "end_time": ,
            }
            for answer in answers
        ]

    return answers


@router.get("/{id}", response_model=schema.Answer)
def get_answer(id: int, db: Session = Depends(get_db)):
    answer = db.query(model.Answer).get(id)
    log(log.INFO, f"get_answer: answer [{id}] exists: {bool(answer)}")

    if not answer:
        log(log.ERROR, f"get_answer: answer [{id}] doesn't exist")
        raise HTTPException(
            status_code=404, detail="get_question: This answer was not found"
        )
    return answer


@router.delete("/{id}", status_code=204)
def delete_answer(
    id: int,
    db: Session = Depends(get_db),
):
    deleted_answer = db.query(model.Answer).filter_by(id=id).first()
    log(log.INFO, f"delete_answer: answer [{id}] exists: {bool(deleted_answer)}")

    if not deleted_answer:
        log(log.ERROR, f"delete_answer: answer [{id}] doesn't exists")
        raise HTTPException(
            status_code=404, detail="delete_question: This answer was not found"
        )
    db.delete(deleted_answer)
    db.commit()
    log(log.INFO, f"delete_answer: answer [{id}] was deleted")

    return Response(status_code=204)


@router.put("/{id}", response_model=schema.Answer)
def update_answer(
    id: int,
    question_info: schema.AnswerCreate,
    db: Session = Depends(get_db),
):
    update_answer = db.query(model.Answer).filter_by(id=id)
    log(log.INFO, f"update_answer: answer [{id}] exists: {bool(update_answer.first())}")

    if not update_answer.first():
        log(log.ERROR, f"update_answer: answer [{id}] doesn't exists")
        raise HTTPException(
            status_code=404, detail="update_question: This answer was not found"
        )

    update_answer.update(question_info.dict(), synchronize_session=False)
    db.commit()
    log(log.INFO, f"update_answer: answer [{id}] was updated")

    return update_answer.first()
