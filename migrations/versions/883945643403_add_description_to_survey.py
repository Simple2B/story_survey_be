"""add description to survey

Revision ID: 883945643403
Revises: 02747d495e31
Create Date: 2022-06-26 21:49:07.223161

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '883945643403'
down_revision = '02747d495e31'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('surveys', sa.Column('description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('surveys', 'description')
    # ### end Alembic commands ###