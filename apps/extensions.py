# coding: utf-8
# 📂 apps/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy import MetaData

# تعريف الـ Naming Convention
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
    تم تعديل الترتيب لمنع تداخل صلاحيات الإدارة مع الموردين.
    """
    from apps.models.admin_db import AdminUser
    from apps.models.supplier_staff_db import SupplierStaff
    from apps.models.marketer_db import Marketer
    
    try:
        uid = int(user_id)
        
        # 1. البحث عن المورد أولاً (لأننا نعمل على لوحة المورد)
        user = SupplierStaff.query.get(uid)
        if user: return user
        
        # 2. البحث عن المسوق
        user = Marketer.query.get(uid)
        if user: return user

        # 3. البحث عن الإدارة أخيراً
        user = AdminUser.query.get(uid)
        if user: return user
        
    except (ValueError, Exception):
        return None
    
    return None

# إعداد مسار تسجيل الدخول الموحد
login_manager.login_view = 'auth_portal.login'
login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى لوحة التحكم."
login_manager.login_message_category = "info"
