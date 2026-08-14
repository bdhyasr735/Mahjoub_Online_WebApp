# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/registry.py
"""
تسجيل موديول الرقابة المالية (الخزينة المركزية) في لوحة الإدارة الرئيسية
مشروع Mahjoub Online WebApp
"""

MODULE_NAME = "الرقابة المالية"
MODULE_ICON = "fas fa-vault"
SHOW_IN_ADMIN = True

# روابط القائمة الجانبية المتوافقة مع هيكل القالب الأساسي
LINKS = {
    'admin_treasury.treasury_index': 'الخزينة المركزية والقيود'
}

def register_module(app):
    from apps.admin_treasury import admin_treasury_bp
    
    if 'admin_treasury' not in app.blueprints:
        app.register_blueprint(admin_treasury_bp, url_prefix='/admin/treasury')
