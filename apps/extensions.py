# coding: utf-8
# 📂 apps/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy import MetaData

# تعريف الـ Naming Convention (اتفاقية التسمية) - صمام أمان لقاعدة البيانات
metadata = MetaData(
    naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }
)

db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
login_manager = LoginManager()

# [صمام الأمان لـ Flask-Login]: تعريف دالة تحميل المستخدم لمنع خطأ 500
@login_manager.user_loader
def load_user(user_id):
    """
    دالة موحدة لتحميل المستخدمين من الموديلات المختلفة.
    يتم استيراد الموديلات هنا (Lazy Import) لمنع الـ Circular Imports.
    """
    from apps.models.admin_db import AdminUser
    from apps.models.supplier_staff_db import SupplierStaff
    from apps.models.marketers_db import Marketer
    
    # محاولة البحث في كل موديول على حدة
    user = AdminUser.query.get(int(user_id))
    if user: return user
    
    user = SupplierStaff.query.get(int(user_id))
    if user: return user
    
    user = Marketer.query.get(int(user_id))
    if user: return user
    
    return None

# إعداد مسار تسجيل الدخول غير المصرح به
login_manager.login_view = 'auth_portal.login'
