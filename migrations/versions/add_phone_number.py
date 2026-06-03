# محتوى ملف الهجرة (داخل مجلد migrations/versions/)
from alembic import op
import sqlalchemy as sa

def upgrade():
    # هذا الأمر يُنفذ عند تحديث القاعدة
    op.add_column('admin_users', sa.Column('phone_number', sa.String(length=20), nullable=False))

def downgrade():
    # هذا الأمر يُنفذ إذا أردت التراجع عن التحديث
    op.drop_column('admin_users', 'phone_number')
