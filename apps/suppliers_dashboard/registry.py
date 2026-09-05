# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)

MODULE_NAME = "لوحة تحكم الموردين"
MODULE_ICON = "fas fa-home"
SHOW_IN_SUPPLIER = True

class SuppliersDashboardRegistry:
    def __init__(self, app=None):
        self.modules = {}
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        self.app = app
        logger.info("تم تهيئة مسجل لوحة الموردين (SuppliersDashboardRegistry) بنجاح.")

    def register_module(self, key, config):
        if key in self.modules:
            logger.warning(f"الموديول '{key}' مسجل مسبقاً، سيتم تحديثه.")
        self.modules[key] = config

    def get_modules(self):
        return self.modules

suppliers_registry = SuppliersDashboardRegistry()
