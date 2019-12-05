"""empty message

Revision ID: 825d6e403275
Revises: 9e578d274c18
Create Date: 2019-12-05 11:04:36.926554

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '825d6e403275'
down_revision = '9e578d274c18'
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
    op.drop_table('user')
    op.add_column('answer', sa.Column('person_id', sa.Integer(), nullable=False))
    op.drop_constraint('answer_user_id_fkey', 'answer', type_='foreignkey')
    op.create_foreign_key(None, 'answer', 'person', ['person_id'], ['id'])
    op.drop_column('answer', 'user_id')
    op.add_column('question', sa.Column('person_id', sa.Integer(), nullable=True))
    op.drop_constraint('question_user_id_fkey', 'question', type_='foreignkey')
    op.create_foreign_key(None, 'question', 'person', ['person_id'], ['id'])
    op.drop_column('question', 'user_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('question', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'question', type_='foreignkey')
    op.create_foreign_key('question_user_id_fkey', 'question', 'user', ['user_id'], ['id'])
    op.drop_column('question', 'person_id')
    op.add_column('answer', sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'answer', type_='foreignkey')
    op.create_foreign_key('answer_user_id_fkey', 'answer', 'user', ['user_id'], ['id'])
    op.drop_column('answer', 'person_id')
    op.create_table('user',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('password', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='user_pkey')
    )
    op.drop_table('person')
    # ### end Alembic commands ###