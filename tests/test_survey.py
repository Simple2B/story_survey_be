from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import model, schema
from .helper import create_user


def test_create_survey(client: TestClient, db: Session):
    data = create_user()
    # create new user
    response = client.post("/backend/user/create_user", json=data.dict())
    assert response

    new_user = response.json()
    user = db.query(model.User).get(new_user["id"])
    assert user.username == new_user["username"]

    # login by username and password
    response = client.post(
        "/backend/login", data=dict(username=data.username, password=data.password)
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
    data = schema.SurveyCreate(
        title=TITLE,
        user_id=USER_ID,
    )

    response = client.post("/backend/survey/", json=data.dict())
    assert response
    create_survey = response.json()

    # get survey
    survey_id = create_survey["id"]
    response = client.get(f"/backend/survey/{survey_id}")
    assert response
    survey = response.json()
    assert survey["user_id"] == USER_ID

    # get surveys
    response = client.get("/backend/survey/")
    assert response
    surveys = response.json()
    assert len(surveys) == 1
