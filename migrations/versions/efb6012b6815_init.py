"""init

Revision ID: 7016278fde62
Revises: 
Create Date: 2022-07-12 19:09:57.700063

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "efb6012b6815"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("timestamp_session_start", sa.DateTime(), nullable=True),
        sa.Column("timestamp_session_end", sa.DateTime(), nullable=True),
        sa.Column("session", sa.String(length=628), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("username", sa.String(length=628), nullable=True),
        sa.Column("image", sa.String(length=628), nullable=True),
        sa.Column("email", sa.String(length=628), nullable=False),
        sa.Column("password_hash", sa.String(length=628), nullable=True),
        sa.Column("role", sa.Enum("Admin", "Client", name="userrole"), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_table(
        "stripe_data",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("customer_id", sa.String(length=628), nullable=True),
        sa.Column("session_id", sa.String(length=628), nullable=True),
        sa.Column(
            "subscription",
            sa.Enum("Basic", "Advance", name="subscriptiontype"),
            nullable=True,
        ),
        sa.Column("subscription_id", sa.String(length=628), nullable=True),
        sa.Column("product_id", sa.String(length=628), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "surveys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", sa.String(length=36), nullable=True),
        sa.Column("title", sa.String(length=628), nullable=False),
        sa.Column("description", sa.String(length=1256), nullable=True),
        sa.Column("successful_message", sa.String(length=628), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("published", sa.Boolean(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "questions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("question", sa.String(length=628), nullable=False),
        sa.Column("survey_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["survey_id"],
            ["surveys.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "answers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("answer", sa.String(length=628), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("question_id", sa.Integer(), nullable=True),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["question_id"],
            ["questions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["session_id"],
            ["sessions.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("answers")
    op.drop_table("questions")
    op.drop_table("surveys")
    op.drop_table("stripe_data")
    op.drop_table("users")
    op.drop_table("sessions")
    # ### end Alembic commands ###