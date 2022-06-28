from fastapi import HTTPException, Response, Depends, APIRouter
from typing import List
from app import model, schema
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/backend/answer", tags=["Answers"])


@router.get("/", response_model=List[schema.Answer])
def get_answers(db: Session = Depends(get_db)):
    answers = db.query(model.Question).all()
    return answers


@router.post("/create_answer", status_code=201, response_model=List[schema.Answer])
def create_answer(
    answer_info: List[schema.AnswerCreate],
    db: Session = Depends(get_db),
):
    answers = []
    for item in answer_info:
        new_answer = model.Answer(
            answer=item.answer,
            question_id=item.question.id,
        )
        db.add(new_answer)
        db.commit()
        db.refresh(new_answer)
        answers.append(new_answer)

    if len(answers) > 0:
        answers = [
            {
                "id": answer.id,
                "answer": answer.answer,
                "survey_id": answer.question.survey_id,
                "created_at": answer.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
            }
            for answer in answers
        ]

    return answers


@router.get("/{id}", response_model=schema.Answer)
def get_answer(id: int, db: Session = Depends(get_db)):
    answer = db.query(model.Answer).get(id)
    if not answer:
        raise HTTPException(
            status_code=404, detail="get_question: This answer was not found"
        )
    return answer


@router.delete("/{id}", status_code=204)
def delete_answer(
    id: int,
    db: Session = Depends(get_db),
):
    deleted_answer = db.query(model.Answer).filter_by(id=id)
    if not deleted_answer.first():
        raise HTTPException(
            status_code=404, detail="delete_question: This answer was not found"
        )
    deleted_answer.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=204)


@router.put("/{id}", response_model=schema.Answer)
def update_answer(
    id: int,
    question_info: schema.AnswerCreate,
    db: Session = Depends(get_db),
):
    update_answer = db.query(model.Answer).filter_by(id=id)

    if not update_answer.first():
        raise HTTPException(
            status_code=404, detail="update_question: This answer was not found"
        )

    update_answer.update(question_info.dict(), synchronize_session=False)
    db.commit()

    return update_answer.first()
