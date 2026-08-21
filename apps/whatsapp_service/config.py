# coding: utf-8
# 📂 apps/whatsapp_service/config.py

"""
WhatsApp Service Configuration Module for Mahgoob Online
Inherits and provides specific configurations for WhatsApp and Meta APIs.
"""

import os
from flask import current_app

class WhatsAppServiceConfig:
    """إعدادات خدمة الواتساب المحلية داخل الخدمة"""
    
    @staticmethod
    def get_whatsapp_token():
        try:
            return current_app.config.get('WHATSAPP_ACCESS_TOKEN', os.environ.get('WHATSAPP_ACCESS_TOKEN', ''))
        except RuntimeError:
            return os.environ.get('WHATSAPP_ACCESS_TOKEN', '')

    @staticmethod
    def get_phone_number_id():
        try:
            return current_app.config.get('WHATSAPP_PHONE_NUMBER_ID', os.environ.get('WHATSAPP_PHONE_NUMBER_ID', ''))
        except RuntimeError:
            return os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')

    @staticmethod
    def get_business_account_id():
        try:
            return current_app.config.get('WHATSAPP_BUSINESS_ACCOUNT_ID', os.environ.get('WHATSAPP_BUSINESS_ACCOUNT_ID', ''))
        except RuntimeError:
            return os.environ.get('WHATSAPP_BUSINESS_ACCOUNT_ID', '')

    @staticmethod
    def get_verify_token():
        try:
            return current_app.config.get('WHATSAPP_VERIFY_TOKEN', os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token'))
        except RuntimeError:
            return os.environ.get('WHATSAPP_VERIFY_TOKEN', 'mahjoub_secure_webhook_token')

    @staticmethod
    def get_api_version():
        try:
            return current_app.config.get('WHATSAPP_API_VERSION', os.environ.get('WHATSAPP_API_VERSION', 'v20.0'))
        except RuntimeError:
            return os.environ.get('WHATSAPP_API_VERSION', 'v20.0')
