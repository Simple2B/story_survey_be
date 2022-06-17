from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import model, schema
from .helper import create_user


def test_auth(client: TestClient, db: Session):
    # data = {"username": USER_NAME, "email": USER_EMAIL, "password": USER_PASSWORD}
    data = create_user()
    # create new user
    response = client.post("/backend/user/", json=data.dict())
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

    # get user by id
    id = new_user["id"]
    response = client.get(f"/backend/user/{id}", headers=headers)
    assert response and response.ok
    user = response.json()
    assert user["username"] == data.username


def test_req_user(client: TestClient, db: Session):
    req_user = create_user()
    response = client.post("/backend/user/", json=req_user.dict())
    assert response
    assert response.ok
