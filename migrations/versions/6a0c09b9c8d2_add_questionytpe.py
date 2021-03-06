"""add questionytpe

Revision ID: 6a0c09b9c8d2
Revises: 367e2ded7ca7
Create Date: 2020-01-22 08:32:01.921888

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a0c09b9c8d2'
down_revision = '367e2ded7ca7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('type',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('question', sa.Column('type_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'question', 'type', ['type_id'], ['id'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'question', type_='foreignkey')
    op.drop_column('question', 'type_id')
    op.drop_table('type')
    # ### end Alembic commands ###
