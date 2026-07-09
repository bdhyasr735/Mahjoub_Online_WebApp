# coding: utf-8
# 📂 apps/extensions.py - إعداد الإضافات المركزية

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from sqlalchemy import MetaData
from flask import session

# تعريف الـ Naming Convention لمنع تعارض الأسماء في قاعدة البيانات
# هذا يسهل جداً على Alembic إدارة التغييرات في الجداول
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

@login_manager.user_loader
def load_user(user_id):
    """
    دالة موحدة لتحميل المستخدمين بناءً على نوعهم في الجلسة.
    تستخدم الاستيراد المحلي (Local Import) لمنع الحلقات المفرغة.
    """
    try:
        # استيراد محلي لتجنب الـ Circular Import
        from apps.models.admin_db import AdminUser
        from apps.models.supplier_db import Supplier
        from apps.models.supplier_staff_db import SupplierStaff
        from apps.models.marketer_db import Marketer
        
        uid = int(user_id)
        user_type = session.get('user_type')
        
        # البحث بناءً على النوع المحدّد في الجلسة (الأكثر كفاءة وأماناً)
        if user_type == 'admin': return db.session.get(AdminUser, uid)
        if user_type == 'supplier': return db.session.get(Supplier, uid)
        if user_type == 'staff': return db.session.get(SupplierStaff, uid)
        if user_type == 'marketer': return db.session.get(Marketer, uid)
        
        # البحث الشامل في حال عدم وجود Session (للاستعادة أو الحالات الاستثنائية)
        return (db.session.get(Supplier, uid) or 
                db.session.get(SupplierStaff, uid) or 
                db.session.get(Marketer, uid) or 
                db.session.get(AdminUser, uid))
                
    except (ValueError, TypeError, Exception):
        return None

# إعدادات تسجيل الدخول
login_manager.login_view = 'auth_portal.login'
login_manager.login_message = "يرجى تسجيل الدخول للوصول إلى لوحة التحكم."
login_manager.login_message_category = "info"
