import os
import re
import io
import csv
from dotenv import load_dotenv
from fastapi import HTTPException, Response, Depends, APIRouter
from typing import List
from app import model, schema
from app.database import get_db
from sqlalchemy.orm import Session
from app.logger import log
from starlette.responses import StreamingResponse

router = APIRouter(prefix="/backend/survey", tags=["Surveys"])

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"))


@router.get("/surveys", response_model=List[schema.Survey])
def get_surveys(db: Session = Depends(get_db)):
    surveys = db.query(model.Survey).all()
    log(log.INFO, "get_surveys: count surveys [%s]", len(surveys))

    surveys_with_question = []
    if not surveys:
        log(log.INFO, "get_surveys: surveys count [%d]", len(surveys))
        return surveys_with_question

    surveys.sort(key=lambda survey: survey.created_at, reverse=True)

    for survey in surveys:
        questions = (
            db.query(model.Question).filter(model.Question.survey_id == survey.id).all()
        )
        for item in questions:
            if item.question == "":
                questions.remove(item)
                questions.append(item)

        # questions = [item for item in questions if item.question]

        log(log.INFO, "get_surveys: count of questions [%d]", len(questions))

        questions_with_answers = []
        for question in questions:
            answers = (
                db.query(model.Answer)
                .filter(model.Answer.question_id == question.id)
                .all()
            )

            if len(answers) > 0:
                answers = [
                    {
                        "id": answer.id,
                        "question_id": answer.question_id,
                        "answer": answer.answer,
                        "session": answer.session.session,
                    }
                    for answer in answers
                ]
                log(
                    log.INFO,
                    "get_surveys: answer [%d] for question [%d]",
                    len(answers),
                    question.id,
                )

            question = {
                "id": question.id,
                "question": question.question,
                "answers": answers,
                "survey_id": question.survey_id,
            }
            questions_with_answers.append(question)

        surveys_with_question.append(
            {
                "id": survey.id,
                "uuid": survey.uuid,
                "description": survey.description,
                "title": survey.title,
                "created_at": survey.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                "user_id": survey.user_id,
                "email": survey.user.email,
                "questions": questions_with_answers,
                "successful_message": survey.successful_message
                if survey.successful_message
                else "",
                "published": survey.published,
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

    surveys_with_question = []
    if not surveys:
        log(log.INFO, f"get_survey: user {user.id} didn't have surveys")
        return surveys_with_question

    log(log.INFO, "get_survey: surveys count [%d]", len(surveys))
    surveys.sort(key=lambda survey: survey.created_at, reverse=True)

    for survey in surveys:
        questions = (
            db.query(model.Question).filter(model.Question.survey_id == survey.id).all()
        )

        for item in questions:
            if item.question == "":
                questions.remove(item)
                questions.append(item)

        questions = [{"id": item.id, "question": item.question} for item in questions]

        # questions = sorted(questions, key=lambda x: x["id"])

        surveys_with_question.append(
            {
                "id": survey.id,
                "uuid": survey.uuid,
                "title": survey.title,
                "description": survey.description,
                "created_at": survey.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
                "user_id": survey.user_id,
                "email": user.email,
                "questions": questions,
                "successful_message": survey.successful_message
                if survey.successful_message
                else "",
                "published": survey.published,
            }
        )

    return surveys_with_question


@router.post("/create_survey", status_code=201, response_model=schema.Survey)
def create_survey(
    survey: schema.SurveyCreate,
    db: Session = Depends(get_db),
):
    user = db.query(model.User).filter(model.User.email == survey.email).first()
    if not user:
        log(log.ERROR, "User with this key not found")
        return

    log(log.INFO, "create_survey: user [%s]", user)

    new_survey: model.Survey = model.Survey(
        title=survey.title,
        description=survey.description,
        successful_message=survey.successful_message,
        user_id=user.id,
        published=survey.published,
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

    return {
        "id": new_survey.id,
        "uuid": new_survey.uuid,
        "title": new_survey.title,
        "description": new_survey.description,
        "successful_message": new_survey.successful_message,
        "created_at": new_survey.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
        "user_id": new_survey.user_id,
        "questions": new_survey.questions,
        "published": new_survey.published,
    }


@router.get("/get_survey/{id}", response_model=schema.Survey)
def get_survey(id: str, db: Session = Depends(get_db)):
    survey_id = int(re.search(r"\d+", id).group())
    survey = db.query(model.Survey).get(survey_id)

    if not survey:
        raise HTTPException(status_code=404, detail="This survey was not found")

    log(log.INFO, "get_survey: survey [%s]", survey)
    questions = (
        db.query(model.Question).filter(model.Question.survey_id == survey.id).all()
    )
    log(log.INFO, "get_survey: questions [%s]", questions)

    return {
        "id": survey.id,
        "uuid": survey.uuid,
        "title": survey.title,
        "description": survey.description,
        "successful_message": survey.successful_message,
        "created_at": survey.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
        "user_id": survey.user_id,
        "email": survey.user.email,
        "questions": questions,
    }


@router.get("/get_survey_with_uuid/{uuid}", response_model=schema.Survey)
def get_not_public_survey(uuid: str, db: Session = Depends(get_db)):

    survey = db.query(model.Survey).filter(model.Survey.uuid == uuid).first()

    if not survey:
        raise HTTPException(status_code=404, detail="This survey was not found")

    log(log.INFO, "get_survey: survey [%s]", survey)
    questions = (
        db.query(model.Question).filter(model.Question.survey_id == survey.id).all()
    )
    log(log.INFO, "get_survey: questions [%s]", questions)

    if len(questions) > 1:
        # questions.sort(key=lambda x: x.id)
        questions = sorted(questions, key=lambda x: (x.question == "", x.question))

    return {
        "id": survey.id,
        "uuid": survey.uuid,
        "title": survey.title,
        "description": survey.description,
        "successful_message": survey.successful_message,
        "created_at": survey.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
        "user_id": survey.user_id,
        "email": survey.user.email,
        "questions": questions,
        "published": survey.published,
    }


@router.get("/get_survey/survey_with_answer/{id}", response_model=schema.Survey)
def get_survey_with_answer(id: int, db: Session = Depends(get_db)):
    # survey_id = int(re.search(r"\d+", id).group())
    survey = db.query(model.Survey).get(id)

    if not survey:
        raise HTTPException(status_code=404, detail="This survey was not found")

    log(log.INFO, "get_survey_with_answer: survey [%s]", survey)
    questions = (
        db.query(model.Question).filter(model.Question.survey_id == survey.id).all()
    )

    if len(questions) > 1:
        questions = sorted(questions, key=lambda x: (x.question == "", x.question))

    log(log.INFO, "get_survey_with_answer: questions [%s]", questions)

    return {
        "id": survey.id,
        "uuid": survey.uuid,
        "title": survey.title,
        "description": survey.description,
        "successful_message": survey.successful_message,
        "created_at": survey.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
        "user_id": survey.user_id,
        "email": survey.user.email,
        "questions": [
            {
                "id": item.id,
                "question": item.question,
                "survey_id": item.survey_id,
                "survey": item.survey,
                "answers": item.answers,
            }
            for item in questions
        ],
    }


@router.post("/delete_survey", status_code=204)
def delete_survey(
    data: schema.SurveyDelete,
    db: Session = Depends(get_db),
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

                for question in questions.all():
                    answer = db.query(model.Answer).filter(
                        (model.Answer.question_id == question.id)
                    )
                    log(
                        log.INFO, "delete_survey:  answer count [%d]", len(answer.all())
                    )
                    if len(answer.all()) > 0:
                        answer.delete(synchronize_session=False)
                        db.commit()
                        log(log.INFO, "delete_survey:  answer deleted")
                if len(questions.all()):
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


@router.put("/update/{id}", response_model=schema.Survey)
def update_survey(
    id: int,
    survey: schema.SurveyCreate,
    db: Session = Depends(get_db),
    # current_user: int = Depends(oauth2.get_current_user),
):
    user = db.query(model.User).filter(model.User.email == survey.email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User with this key not found")

    updated_survey = db.query(model.Survey).filter_by(id=id)
    # update_question

    if not updated_survey.first():
        raise HTTPException(status_code=404, detail="This survey was not found")

    edit_survey = updated_survey.first()

    updated_questions = (
        db.query(model.Question)
        .filter(model.Question.survey_id == edit_survey.id)
        .all()
    )
    new_questions = survey.questions

    deleted_questions = survey.questions_deleted

    create_question = survey.create_question

    data_edit_survey = {
        "title": survey.title,
        "description": survey.description,
        "successful_message": survey.successful_message,
        "published": survey.published,
        "user_id": user.id,
    }

    for item in new_questions:
        updated_questions = sorted(
            updated_questions, key=lambda x: (x.question == "", x.question)
        )
        # updated_questions = updated_questions[:-1]
        for updated_question in updated_questions:
            if updated_question.id == item["id"]:
                updated_question.question = item["question"]
                updated_question.survey_id = edit_survey.id
                db.commit()
                db.refresh(updated_question)

        updated_questions = sorted(updated_questions, key=lambda x: x.id)

        updated_survey.update(data_edit_survey, synchronize_session=False)
        db.commit()

    if len(deleted_questions) > 0:
        for question in deleted_questions:
            answers = db.query(model.Answer).filter(
                model.Answer.question_id == question["id"]
            )
            if len(answers.all()) > 0:
                answers.delete()
                db.commit()
                log(log.INFO, "update_survey:  answers deleted")

            deleted_question = db.query(model.Question).filter(
                model.Question.id == question["id"]
            )
            deleted_question.delete()
            db.commit()
            # db.refresh(deleted_question)
        log(log.INFO, "update_survey: questions deleted")

        updated_survey.update(data_edit_survey, synchronize_session=False)
        db.commit()

    if len(create_question) > 0:
        for question in create_question:
            new_question = model.Question(
                question=question,
                survey_id=survey.id,
            )
            db.add(new_question)
            db.commit()
            db.refresh(new_question)
            log(
                log.INFO,
                f"update_survey: question '{question}' created for survey {question}",
            )
        updated_survey.update(data_edit_survey, synchronize_session=False)
        db.commit()

    data_survey = updated_survey.first()
    questions = (
        db.query(model.Question)
        .filter(model.Question.survey_id == data_survey.id)
        .all()
    )

    new_data_survey = {
        "created_at": data_survey.created_at.strftime("%m/%d/%Y, %H:%M:%S"),
        "description": data_survey.description,
        "successful_message": data_survey.successful_message,
        "email": user.email,
        "id": data_survey.id,
        "questions": questions,
        "title": data_survey.title,
        "user_id": user.id,
    }

    return new_data_survey


@router.get("/report_survey/{uuid}", response_class=StreamingResponse)
async def formed_report_survey(uuid: str, db: Session = Depends(get_db)):
    """Get for admin report survey data"""
    survey = db.query(model.Survey).filter(model.Survey.uuid == uuid).first()
    report_file = io.StringIO()

    report = csv.writer(report_file)
    data = [["user", "title", "description", "created_at", "published"]]

    data_questions = []

    survey_id = survey.id
    survey_user = survey.user.email
    survey_title = survey.title
    survey_description = survey.description
    survey_created_at = survey.created_at.strftime("%H:%M:%S %b %d %Y")
    survey_published = survey.published

    survey_questions = (
        db.query(model.Question).filter(model.Question.survey_id == survey_id).all()
    )

    questions_answers = []

    if len(survey_questions) > 0:
        for item in survey_questions:
            answers = (
                db.query(model.Answer).filter(model.Answer.question_id == item.id).all()
            )
            questions_answers.append(
                {
                    "question": item.question,
                    "answers": [data_answer.answer for data_answer in answers],
                }
            )

    # survey_questions = [
    #     {"question": survey.question, "answers": survey.answers}
    #     for survey in survey_questions
    #     if survey.question
    # ]

    data.append(
        [
            survey_user,
            survey_title,
            survey_description,
            survey_created_at,
            survey_published,
        ],
    )
    data_questions.append(["questions"])
    for item in questions_answers:
        data_questions.append([item["question"], item["answers"]])
    log(
        log.INFO,
        "formed_report_survey: create report data [%s]",
        data,
    )
    report.writerows(data)
    report.writerows(data_questions)

    buf = io.BytesIO()
    buf.write(report_file.getvalue().encode())
    buf.seek(0)

    buf.name = "report_survey.csv"

    return StreamingResponse(buf, media_type="text/csv")


@router.post("/info_survey", response_model=bool)
def check_answer_the_question(
    req_data: schema.SurveyNextSession, db: Session = Depends(get_db)
):
    survey = db.query(model.Survey).filter(model.Survey.uuid == req_data.uuid).first()
    if not survey:
        log(log.INFO, "get_answer_next_session_of_survey: survey not found")
        return "Survey not found"

    log(log.INFO, f"get_answer_next_session_of_survey: [{survey.id}] survey exist")

    questions = survey.questions
    if len(questions) > 0:
        for question in questions:
            answers = question.answers
            if len(answers) > 0:
                sessions = []
                for answer in answers:
                    session = answer.session.session
                    if session == req_data.session:
                        sessions.append(session)
                if len(sessions) > 0:
                    return True

    return False
