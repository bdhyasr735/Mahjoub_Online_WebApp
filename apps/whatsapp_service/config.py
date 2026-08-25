# coding: utf-8
# 📂 apps/whatsapp_service/config.py

import os
from flask import current_app

class WhatsAppServiceConfig:
    """إعدادات خدمة الواتساب المحلية ومطابقة المتغيرات البيئية بدقة ومرونة"""

    @classmethod
    def _get_val(cls, *keys, default=''):
        # 1. محاولة الجلب من ملف البيئة (.env / Railway Environment Variables) أولاً
        for k in keys:
            env_val = os.environ.get(k)
            if env_val:
                return str(env_val).strip()

        # 2. محاولة الجلب من إعدادات تطبيق Flask
        for k in keys:
            try:
                if current_app:
                    val = current_app.config.get(k)
                    if val:
                        return str(val).strip()
            except RuntimeError:
                pass

        # 3. محاولة الجلب من قاعدة البيانات أخيراً
        try:
            from apps.models.whatsapp_models import WhatsAppSettings
            for k in keys:
                db_val = WhatsAppSettings.get_setting(k)
                if db_val:
                    return str(db_val).strip()
        except Exception:
            pass
            
        return default

    @classmethod
    def get_whatsapp_token(cls):
        # ✅ دعم كافة الاحتمالات لاسم التوكن
        return cls._get_val('WHATSAPP_ACCESS_TOKEN', 'WHATSAPP_TOKEN', 'WHATSAPP ACCESS TOKEN')

    @classmethod
    def get_phone_number_id(cls):
        return cls._get_val('WHATSAPP_PHONE_NUMBER_ID', 'WHATSAPP PHONE NUMBER ID', default='1336881386166971')

    @classmethod
    def get_business_account_id(cls):
        return cls._get_val('WHATSAPP_BUSINESS_ACCOUNT_ID', 'WHATSAPP BUSINESS ACCOUNT ID', default='2280533956048577')

    @classmethod
    def get_verify_token(cls):
        return cls._get_val('WHATSAPP_VERIFY_TOKEN', 'WHATSAPP VERIFY TOKEN', default='mahjoob_webhook_secret_2026')

    @classmethod
    def get_webhook_secret(cls):
        return cls._get_val('WEBHOOK_SECRET', 'WEBHOOK SECRET')

    @classmethod
    def get_api_version(cls):
        return cls._get_val('WHATSAPP_API_VERSION', default='v21.0')
