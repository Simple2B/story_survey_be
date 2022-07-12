from sqlalchemy.orm import Session
from invoke import task
from app.config import settings
from app import model

NUM_TEST_USERS = 10
NUM_TEST_POSTS = 3

admins = [
    {
        "username": settings.ADMIN_USER,
        "password": settings.ADMIN_PASS,
        "email": settings.ADMIN_EMAIL,
        "role": model.User.UserRole.Admin,
    },
    {
        "username": settings.ADMIN2_USER,
        "password": settings.ADMIN2_PASS,
        "email": settings.ADMIN2_EMAIL,
        "role": model.User.UserRole.Admin,
    },
    {
        "username": settings.ADMIN3_USER,
        "password": settings.ADMIN3_PASS,
        "email": settings.ADMIN3_EMAIL,
        "role": model.User.UserRole.Admin,
    },
]


@task
def init_db(_, test_data=False):
    """Initialization database

    Args:
        --test-data (bool, optional): wether fill database by test data. Defaults to False.
    """
    from app.database import SessionLocal

    db = SessionLocal()
    # add admin user
    # admin = db.query(User).filter(User.email == settings.ADMIN_EMAIL).first()
    # if not admin:
    for item in range(len(admins)):
        admin = (
            db.query(model.User)
            .filter(model.User.email == admins[item]["email"])
            .first()
        )
        if admin:
            admin.username = admins[item]["username"]
            admin.password = admins[item]["password"]
            admin.email = admins[item]["email"]
            admin.role = admins[item]["role"]
            db.add(admin)

        admin: model.User = model.User(
            username=admins[item]["username"],
            password=admins[item]["password"],
            email=admins[item]["email"],
            role=admins[item]["role"],
        )
        db.add(admin)
    if test_data:
        # Add test data
        fill_test_data(db)

    db.commit()


def fill_test_data(db: Session):
    from app.model import Survey

    for uid in range(NUM_TEST_USERS):
        user = User(username=f"User{uid}", password="pa$$", email=f"user{uid}@test.com")
        db.add(user)
        db.commit()
        db.refresh(user)
        for pid in range(NUM_TEST_POSTS):
            db.add(
                Survey(
                    title=f"Title{pid}",
                    user_id=user.id,
                )
            )
