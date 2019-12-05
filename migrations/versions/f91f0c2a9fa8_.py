"""empty message

Revision ID: f91f0c2a9fa8
Revises: af34f0af7d6f
Create Date: 2019-12-05 11:07:34.075924

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f91f0c2a9fa8'
down_revision = 'af34f0af7d6f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('person',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('personname', sa.String(length=255), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('answer', sa.Column('person_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'answer', 'person', ['person_id'], ['id'])
    op.drop_column('answer', 'user_id')
    op.add_column('question', sa.Column('person_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'question', 'person', ['person_id'], ['id'])
    op.drop_column('question', 'user_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('question', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'question', type_='foreignkey')
    op.drop_column('question', 'person_id')
    op.add_column('answer', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'answer', type_='foreignkey')
    op.drop_column('answer', 'person_id')
    op.drop_table('person')
    # ### end Alembic commands ###