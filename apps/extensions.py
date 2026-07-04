# coding: utf-8
# 📂 apps/extensions.py

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy import MetaData

# تعريف الـ Naming Convention لمنع تعارض الأسماء في الجداول
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

# [المخزن المركزي للموديولات]: هذا القاموس سيسجل فيه كل موديول بياناته ليظهر في القائمة الجانبية
registered_modules = {}

# [صمام الأمان لـ Flask-Login]: تعريف دالة تحميل المستخدم المركزية
@login_manager.user_loader
def load_user(user_id):
    """
    دالة موحدة لتحميل المستخدمين من الموديلات المختلفة.
    """
    from apps.models.admin_db import AdminUser
    from apps.models.supplier_db import Supplier
    from apps.models.supplier_staff_db import SupplierStaff
    from apps.models.marketer_db import Marketer
    
    try:
        uid = int(user_id)
        
        # البحث التسلسلي باستخدام db.session.get
        user = db.session.get(Supplier, uid) or \
               db.session.get(SupplierStaff, uid) or \
               db.session.get(Marketer, uid) or \
               db.session.get(AdminUser, uid)
               
        return user
        
    except (ValueError, TypeError, Exception):
        return None

# إعداد مسار تسجيل الدخول الموحد
login_manager.login_view = 'auth_portal.login'
login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى لوحة التحكم."
login_manager.login_message_category = "info"
