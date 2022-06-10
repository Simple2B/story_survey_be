"""model_User

Revision ID: 858baf3b11a0
Revises: 24ed2f337b34
Create Date: 2022-06-10 11:10:47.369835

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '858baf3b11a0'
down_revision = '24ed2f337b34'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('users_username_key', 'users', type_='unique')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('users_username_key', 'users', ['username'])
    # ### end Alembic commands ###
