"""add rescue alert model

Revision ID: 270e8c1fddb9
Revises: 89d623f5b20a
Create Date: 2025-07-10 15:40:04.661509

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '270e8c1fddb9'
down_revision = '89d623f5b20a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rescue_alert',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('location', sa.String(length=256), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('contact', sa.String(length=64), nullable=False),
    sa.Column('landmark', sa.String(length=128), nullable=False),
    sa.Column('animal_type', sa.String(length=32), nullable=False),
    sa.Column('wait_time', sa.String(length=32), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rescue_alert')
    # ### end Alembic commands ###
