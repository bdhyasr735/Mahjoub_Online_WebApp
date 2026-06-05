from apps import create_app # تأكد أن هذا المسار يشير لمجلد مشروعك الرئيسي
from apps.extensions import db

config = context.config
app = create_app()

# هذا الجزء يربط Alembic بقاعدة بيانات Flask
target_metadata = db.metadata

def run_migrations_online():
    connectable = db.engine
    # ... بقية الكود التلقائي
