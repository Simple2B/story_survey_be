from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from .helper import create_user


def test_create_customer(client: TestClient, db: Session):
    """Test for get_history() function from route/history.py"""

    data_frst = create_user()
    data_sec = create_user(name="David", email="newtest@test.com")
    # create new users
    response_frst = client.post("/backend/user/create_user", json=data_frst.dict())
    assert response_frst
    response_sec = client.post("/backend/user/create_user", json=data_sec.dict())
    assert response_sec

    # get history
    response = client.get("/backend/history/")
    assert response.ok
