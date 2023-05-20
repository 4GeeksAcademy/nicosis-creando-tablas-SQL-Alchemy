"""empty message

Revision ID: 858f0ac4c819
Revises: 9ca8a6dc9899
Create Date: 2023-05-19 21:12:15.720580

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '858f0ac4c819'
down_revision = '9ca8a6dc9899'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('project',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_name', sa.String(length=200), nullable=False),
    sa.Column('topics', sa.String(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('project_name'),
    sa.UniqueConstraint('topics')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('project')
    # ### end Alembic commands ###
