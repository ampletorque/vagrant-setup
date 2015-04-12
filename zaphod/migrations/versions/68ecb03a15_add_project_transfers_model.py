from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
"""
Add project transfers model

Revision ID: 68ecb03a15
Revises: 3cf560cb10a
Create Date: 2015-04-12 13:30:38.213986
"""

# revision identifiers, used by Alembic.
revision = '68ecb03a15'
down_revision = '3cf560cb10a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'project_transfers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('amount', 
                  sa.Numeric(precision=10, scale=2),
                  nullable=False),
        sa.Column('fee',
                  sa.Numeric(precision=10, scale=2),
                  nullable=False),
        sa.Column('method', sa.String(length=255), nullable=False),
        sa.Column('reference', sa.Unicode(length=255), nullable=False),
        sa.Column('created_time', sa.DateTime(), nullable=False),
        sa.Column('updated_time', sa.DateTime(), nullable=False),
        sa.Column('updated_by_id', sa.Integer(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['created_by_id'], ['users.id'],
            name=op.f('fk_project_transfers_created_by_id')),
        sa.ForeignKeyConstraint(
            ['project_id'], ['projects.node_id'],
            name=op.f('fk_project_transfers_project_id')),
        sa.ForeignKeyConstraint(
            ['updated_by_id'], ['users.id'],
            name=op.f('fk_project_transfers_updated_by_id')),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_project_transfers')),
        mysql_engine='InnoDB'
    )


def downgrade():
    op.drop_table('project_transfers')
