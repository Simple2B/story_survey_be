"""Survey add published

Revision ID: fd49bd101720
Revises: a78fb5038fe9
Create Date: 2022-06-10 15:26:02.549509

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd49bd101720'
down_revision = 'a78fb5038fe9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('surveys', sa.Column('published', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('surveys', 'published')
    # ### end Alembic commands ###
