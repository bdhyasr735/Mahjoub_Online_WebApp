# -*- coding: utf-8 -*-
# apps/auth_portal/registry.py

"""
مسجل البوابة السيادية الإدارية (Auth Portal Registry)
معتمد صراحةً على جلب وإدارة الكيانات، الجداول، والحقول المرتبطة بالمسار السيادي
"""

import logging
from flask import Flask
from apps.extensions import db

logger = logging.getLogger(__name__)

class AuthPortalRegistry:
    """مسجل يعتمد على الجداول والحقول الخاصة بالمشرفين لتفعيل البوابة السيادية بالمسار الصحيح"""

    def __init__(self, app: Flask = None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        """التحقق من جاهزية جدول وحقول الآدمن وتسجيل الـ Blueprint صراحةً"""
        try:
            # 1. التحقق الفعلي من وجود جدول وحقول المشرفين (AdminUser)
            from apps.models.admin_db import AdminUser
            
            inspector = db.inspect(db.engine)
            table_name = AdminUser.__tablename__
            
            if not inspector.has_table(table_name):
                logger.error(f"❌ [AuthPortalRegistry]: الجدول المطلوب '{table_name}' غير موجود في قاعدة البيانات!")
                return

            columns = [col['name'] for col in inspector.get_columns(table_name)]
            required_columns = ['id', 'username', 'password_hash']
            missing_columns = [col for col in required_columns if col not in columns]

            if missing_columns:
                logger.error(f"❌ [AuthPortalRegistry]: الجدول '{table_name}' يفتقر للحقول التالية: {missing_columns}")
                return

            logger.info(f"✅ [AuthPortalRegistry]: تم التحقق من جدول الحقول '{table_name}' والحقول الأساسية بنجاح.")

            # 2. استيراد وتسجيل الـ Blueprint بالمسار السيادي الأصلي
            from apps.auth_portal.routes import auth_portal_bp
            
            if 'auth_portal_bp' not in app.blueprints:
                app.register_blueprint(auth_portal_bp)
                
                try:
                    from apps.extensions import csrf
                    csrf.exempt(auth_portal_bp)
                except Exception:
                    pass
                    
                logger.info("🛡️ [AuthPortalRegistry]: تم تفعيل المسار السيادي '/m7jb_sovereign_hq_v2_99x' وربطه بالجدول والحقول بنجاح.")
            else:
                logger.debug("ℹ️ [AuthPortalRegistry]: الـ Blueprint مسجل مسبقاً.")

        except Exception as e:
            logger.error(f"❌ [AuthPortalRegistry]: خطأ فادح أثناء التحقق من الجداول والحقول: {str(e)}", exc_info=True)


# كائن التسجيل المعتمد على الجداول
auth_registry = AuthPortalRegistry()
