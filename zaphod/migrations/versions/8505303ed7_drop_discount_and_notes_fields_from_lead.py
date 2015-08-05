"""
Drop discount and notes fields from lead

Revision ID: 8505303ed7
Revises: b3d0ecf493
Create Date: 2015-04-23 23:14:45.550127
"""

# revision identifiers, used by Alembic.
revision = '8505303ed7'
down_revision = 'b3d0ecf493'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.drop_column('leads', 'notes')
    op.drop_column('leads', 'discount')


def downgrade():
    op.add_column('leads', sa.Column('discount', mysql.VARCHAR(length=255),
                                     nullable=False))
    op.add_column('leads', sa.Column('notes', mysql.TEXT(), nullable=False))
