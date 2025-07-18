"""add rescue message model

Revision ID: e99b249e9d1b
Revises: 270e8c1fddb9
Create Date: 2025-07-10 15:48:27.736003

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e99b249e9d1b'
down_revision = '270e8c1fddb9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('rescue_message',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('alert_id', sa.Integer(), nullable=False),
    sa.Column('sender_id', sa.Integer(), nullable=False),
    sa.Column('message', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('read_by_ngo', sa.Boolean(), nullable=True),
    sa.Column('read_by_user', sa.Boolean(), nullable=True),
    sa.Column('attachment', sa.String(length=300), nullable=True),
    sa.ForeignKeyConstraint(['alert_id'], ['rescue_alert.id'], ),
    sa.ForeignKeyConstraint(['sender_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('rescue_message')
    # ### end Alembic commands ###
