# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)

class SuppliersDashboardRegistry:
    """
    مسؤول عن تسجيل المكونات، الوحدات، والصلاحيات الخاصة بلوحة تحكم الموردين 
    في منصة محجوب أونلاين بشكل ديناميكي.
    """
    def __init__(self, app=None):
        self.modules = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        # تسجيل إعدادات النظام أو المكونات الإضافية هنا إن وجدت
        logger.info("تم تهيئة مسجل لوحة الموردين (SuppliersDashboardRegistry) بنجاح.")

    def register_module(self, key, config):
        """تسجيل موديول أو قسم جديد في لوحة التحكم ديناميكياً"""
        if key in self.modules:
            logger.warning(f"الموديول '{key}' مسجل مسبقاً، سيتم تحديثه.")
        self.modules[key] = config

    def get_modules(self):
        """استرجاع كافة الموديولات المسجلة"""
        return self.modules

# كائن عام للمسجل يمكن استيراده في باقي أجزاء التطبيق
suppliers_registry = SuppliersDashboardRegistry()
