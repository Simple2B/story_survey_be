from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import model, schema
from .helper import create_user


def test_get_user(client: TestClient, db: Session):
    """Test for get_user function from router/user.py"""

    # data = {"username": USER_NAME, "email": USER_EMAIL, "password": USER_PASSWORD}
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

    # get user by id
    email = new_user["email"]
    response = client.get(f"/backend/user/email/{email}", headers=headers)
    assert response and response.ok
    user = response.json()
    assert user["username"] == data.username


def test_create_user(client: TestClient, db: Session):
    """Test for create_user function from router/user.py"""

    req_user = create_user()
    response = client.post("/backend/user/create_user", json=req_user.dict())
    assert response
    assert response.ok


def test_get_users(client: TestClient, db: Session):
    """Test for get_users function from router/user.py"""

    # create two new users
    first_new_user = create_user()
    first_new_user = client.post(
        "/backend/user/create_user", json=first_new_user.dict()
    )
    assert first_new_user.ok
    sec_new_user = create_user(name="John", email="john@john.com")
    response_sec = client.post("/backend/user/create_user", json=sec_new_user.dict())
    assert response_sec.ok

    # get created users
    response = client.get("/backend/user/get_users")
    assert response.ok
    response_data = response.json()
    assert len(response_data) == 2
