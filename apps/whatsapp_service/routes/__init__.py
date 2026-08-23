# coding: utf-8
# 📂 apps/whatsapp_service/routes/__init__.py

from flask import Blueprint

# تعريف البلوبرينت باسم 'whatsapp' ليطابق الروابط التي جهزناها
whatsapp_bp = Blueprint('whatsapp', __name__, template_folder='../templates')

# استيراد ملفات المسارات بعد التعريف لتجنب تداخل الاستيراد
from . import dashboard
