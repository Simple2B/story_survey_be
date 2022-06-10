from fastapi import HTTPException, Response, Depends, APIRouter
from typing import List
from app import model, oauth2, schema
from app.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/question", tags=["Questions"])


@router.get("/", response_model=List[schema.Question])
def get_question(db: Session = Depends(get_db)):
    questions = db.query(model.Question).all()
    return questions


@router.post("/", status_code=201, response_model=schema.Question)
def create_question(
    question_info: schema.QuestionCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    new_question = model.Question(
        question=question_info.question,
        survey_id=question_info.survey_id,
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)

    return new_question


@router.get("/{id}", response_model=schema.Question)
def get_question(id: int, db: Session = Depends(get_db)):
    question = db.query(model.Question).get(id)
    if not question:
        raise HTTPException(
            status_code=404, detail="get_question: This question was not found"
        )
    return question


@router.delete("/{id}", status_code=204)
def delete_question(
    id: int,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    deleted_question = db.query(model.Question).filter_by(id=id)
    if not deleted_question.first():
        raise HTTPException(
            status_code=404, detail="delete_question: This question was not found"
        )

    if deleted_question.first().user_id != current_user.id:
        raise HTTPException(
            status_code=403, detail="delete_question: Not enough permissions"
        )

    deleted_question.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=204)


@router.put("/{id}", response_model=schema.Question)
def update_question(
    id: int,
    question_info: schema.QuestionCreate,
    db: Session = Depends(get_db),
    current_user: int = Depends(oauth2.get_current_user),
):
    update_question = db.query(model.Question).filter_by(id=id)

    if not update_question.first():
        raise HTTPException(
            status_code=404, detail="update_question: This question was not found"
        )

    # if update_question.first().user_id != current_user.id:
    #     raise HTTPException(
    #         status_code=403, detail="update_question: Not enough permissions"
    #     )

    update_question.update(question_info.dict(), synchronize_session=False)
    db.commit()

    return update_question.first()
