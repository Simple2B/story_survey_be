from fastapi import HTTPException, Response, Depends, APIRouter
from typing import List
from app import model, oauth2, schema
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/answer", tags=["Answers"])


@router.get("/", response_model=List[schema.Answer])
def get_answers(db: Session = Depends(get_db)):
    answers = db.query(model.Question).all()
    return answers


@router.post("/", status_code=201, response_model=schema.Answer)
def create_answer(
    answer_info: schema.AnswerCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    new_answer = model.Answer(
        answer=answer_info.answer,
        question_id=answer_info.question_id,
    )
    db.add(new_answer)
    db.commit()
    db.refresh(new_answer)

    return new_answer


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
    current_user: int = Depends(oauth2.get_current_user),
):
    deleted_answer = db.query(model.Answer).filter_by(id=id)
    if not deleted_answer.first():
        raise HTTPException(
            status_code=404, detail="delete_question: This answer was not found"
        )

    # if deleted_answer.first().user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=403, detail="delete_question: Not enough permissions"
    #     )

    deleted_answer.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=204)


@router.put("/{id}", response_model=schema.Answer)
def update_answer(
    id: int,
    question_info: schema.AnswerCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    update_answer = db.query(model.Answer).filter_by(id=id)

    if not update_answer.first():
        raise HTTPException(
            status_code=404, detail="update_question: This answer was not found"
        )

    # if update_question.first().user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=403, detail="update_question: Not enough permissions"
    #     )

    update_answer.update(question_info.dict(), synchronize_session=False)
    db.commit()

    return update_answer.first()
