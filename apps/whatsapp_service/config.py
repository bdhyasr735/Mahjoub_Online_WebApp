# coding: utf-8
# 📂 apps/whatsapp_service/config.py

"""
WhatsApp Service Configuration Module for Mahgoob Online
Inherits and provides specific configurations for WhatsApp and Meta APIs.
Supports flexible key lookups with both underscore and spaced variable names.
"""

import os
from flask import current_app

class WhatsAppServiceConfig:
    """إعدادات خدمة الواتساب المحلية ومطابقة المتغيرات البيئية بدقة ومرونة"""

    @classmethod
    def _get_val(cls, *keys, default=''):
        """مساعد للبحث عن القيمة في إعدادات التطبيق أو بيئة التشغيل بعدة مسميات"""
        for k in keys:
            try:
                if current_app:
                    val = current_app.config.get(k)
                    if val:
                        return str(val).strip()
            except RuntimeError:
                pass
            
            env_val = os.environ.get(k)
            if env_val:
                return str(env_val).strip()
        return default

    @classmethod
    def get_whatsapp_token(cls):
        return cls._get_val('WHATSAPP_ACCESS_TOKEN', 'WHATSAPP ACCESS TOKEN')

    @classmethod
    def get_phone_number_id(cls):
        return cls._get_val('WHATSAPP_PHONE_NUMBER_ID', 'WHATSAPP PHONE NUMBER ID', default='1336881386166971')

    @classmethod
    def get_business_account_id(cls):
        return cls._get_val('WHATSAPP_BUSINESS_ACCOUNT_ID', 'WHATSAPP BUSINESS ACCOUNT ID', default='2280533956048577')

    @classmethod
    def get_verify_token(cls):
        return cls._get_val(
            'WHATSAPP_VERIFY_TOKEN', 
            'WHATSAPP VERIFY TOKEN', 
            default='mahjoub secure webhook token'
        )

    @classmethod
    def get_webhook_secret(cls):
        return cls._get_val('WEBHOOK_SECRET', 'WEBHOOK SECRET')

    @classmethod
    def get_twilio_number(cls):
        return cls._get_val('TWILIO_NUMBER', 'TWILIO NUMBER', 'WHATSAPP_PHONE_NUMBER', default='+967779077746')

    @classmethod
    def get_api_version(cls):
        return cls._get_val('WHATSAPP_API_VERSION', default='v21.0')
