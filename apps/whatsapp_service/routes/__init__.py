import os
from flask import Blueprint

# 1. إنشاء الـ Blueprint وتحديد مجلد القوالب
template_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
whatsapp_bp = Blueprint('whatsapp', __name__, template_folder=template_dir)

# 2. استيراد كافة المسارات الفرعية لربطها بـ whatsapp_bp
from apps.whatsapp_service.routes import dashboard
from apps.whatsapp_service.routes import actions
from apps.whatsapp_service.routes import api
from apps.whatsapp_service.routes import webhook
