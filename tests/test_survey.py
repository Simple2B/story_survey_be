from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import model, schema
from .helper import create_user


def test_create_survey(client: TestClient, db: Session):
    """Test for create_survey() function from router/survey.py"""

    data = create_user()
    # create new user
    response = client.post("/backend/user/create_user", json=data.dict())
    assert response

    new_user = response.json()
    user = db.query(model.User).get(new_user["id"])
    assert user.username == new_user["username"]

    # login by username and password
    response = client.post(
        "/backend/user/sign_in",
        data=dict(username=data.username, password=data.password),
    )
    assert response and response.ok, "unexpected response"
    token = schema.Token.parse_obj(response.json())
    headers = {"Authorization": f"Bearer {token.access_token}"}

    id = new_user["id"]

    response = client.get(f"/backend/user/{id}", headers=headers)
    assert response and response.ok
    user = response.json()
    assert user["username"] == data.username

    # create survey for user
    USER_ID = user["id"]
    TITLE = "Survey"
    QUESTIONS = ["Question1", "Question2", "Question3"]
    EMAIL = user["email"]
    data = schema.SurveyCreate(
        title=TITLE, user_id=USER_ID, questions=QUESTIONS, email=EMAIL
    )

    response = client.post("/backend/survey/create_survey", json=data.dict())
    assert response
    create_survey = response.json()
    assert create_survey

    # get surveys for user
    response = client.get(f"/backend/survey/{EMAIL}")
    assert response
    survey = response.json()
    assert survey[0]["user_id"] == USER_ID

    # get surveys
    response = client.get("/backend/survey/surveys/")
    assert response
    surveys = response.json()
    assert len(surveys) == 1

    questions = surveys[0]["questions"]

    # create answer
    answerInfo = []
    for i in range(len(questions)):

        answerInfo.append(
            {
                "answer": f"Answer_{i+1}",
                "question": {
                    "id": questions[i]["id"],
                    "survey_id": questions[i]["survey_id"],
                    "question": questions[i]["question"],
                },
                "email": EMAIL,
            }
        )

    response = client.post("/backend/answer/create_answer", json=answerInfo)
    assert response
    answers = response.json()
    assert answers
    assert len(answers) == 3


def test_get_surveys(client: TestClient, db: Session):
    """Test for get_surveys() function from router/survey.py"""

    data = create_user("Poll", "test@test.ku")
    # create new user
    response = client.post("/backend/user/create_user", json=data.dict())
    assert response
    user = response.json()

    # create survey with question
    info_survey = {
        "title": "Title",
        "description": "Description",
        "user_id": user["id"],
        "email": user["email"],
        "questions": [
            "Question_1",
            "Question_2",
            "Question_3",
            "Question_4",
            "Question_5",
        ],
    }

    response = client.post("/backend/survey/create_survey", json=info_survey)
    assert response
    survey = response.json()
    assert survey["user_id"] == user["id"]

    data_user2 = create_user("Stive", "stive@test.ku")
    # create new user
    response = client.post("/backend/user/create_user", json=data_user2.dict())
    assert response
    user2 = response.json()

    # create surveys with question
    surveys = []
    for i in range(5):
        surveys.append(
            {
                "title": f"Title_{i}",
                "description": f"Description_{i}",
                "user_id": user2["id"],
                "email": user2["email"],
                "questions": [
                    f"Question_1_Title_{i}",
                    f"Question_2_Title_{i}",
                    f"Question_3_Title_{i}",
                    f"Question_4_Title_{i}",
                    f"Question_5_Title_{i}",
                ],
            }
        )
    if len(surveys) > 0:
        for survey in surveys:
            response = client.post("/backend/survey/create_survey", json=survey)
            assert response

    # get all surveys
    response = client.get("/backend/survey/surveys")
    assert response
    all_surveys = response.json()
    assert len(all_surveys) == 6

    email = user2["email"]

    # get surveys for user
    response = client.get(f"/backend/survey/{email}")
    assert response
    user_surveys = response.json()
    assert len(user_surveys) == 5

    survey_to_delete = {
        "survey_id": user_surveys[0]["id"],
        "email": email,
    }

    # delete survey
    response = client.post("/backend/survey/delete_survey", json=survey_to_delete)
    assert response
    assert response.status_code == 204

    # get surveys user after deleted 1 survey
    response = client.get(f"/backend/survey/{email}")
    assert response
    user_surveys = response.json()
    assert len(user_surveys) == 4
