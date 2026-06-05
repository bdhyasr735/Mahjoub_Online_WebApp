# 📂 apps/extensions.py
# الملف المركزي لتعريف إضافات التطبيق (Extensions)

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate  # تم استيراد المكتبة هنا

# تعريف كائنات الإضافات
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()  # تم تعريف كائن المهاجرات هنا ليصبح جاهزاً للاستيراد في __init__.py
