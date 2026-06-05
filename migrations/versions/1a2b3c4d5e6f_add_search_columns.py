"""add_search_columns

Revision ID: 1a2b3c4d5e6f  # (سيكون لديك رقم مختلف)
Revises: None
Create Date: 2026-06-05 ...
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # هنا يضع النظام الأوامر التي أضفتها أنت في كود الـ Model
    op.add_column('suppliers', sa.Column('search_name', sa.String(length=255), nullable=True))
    op.add_column('suppliers', sa.Column('search_phone', sa.String(length=50), nullable=True))

def downgrade():
    # هنا يضع النظام أوامر التراجع
    op.drop_column('suppliers', 'search_name')
    op.drop_column('suppliers', 'search_phone')
