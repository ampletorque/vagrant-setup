"""
Add vendor invoice item fields

Revision ID: 2f6abf8c3e1
Revises: None
Create Date: 2015-04-11 14:57:03.538833
"""

# revision identifiers, used by Alembic.
revision = '2f6abf8c3e1'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('vendor_invoice_items',
                  sa.Column('cost_each',
                            sa.Numeric(precision=10, scale=2),
                            nullable=False))
    op.add_column('vendor_invoice_items',
                  sa.Column('qty_invoiced', sa.Integer(), nullable=False))


def downgrade():
    op.drop_column('vendor_invoice_items', 'qty_invoiced')
    op.drop_column('vendor_invoice_items', 'cost_each')
