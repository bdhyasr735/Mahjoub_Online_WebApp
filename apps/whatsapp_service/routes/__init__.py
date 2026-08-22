# coding: utf-8
# 📂 apps/whatsapp_service/routes/__init__.py

import os
from flask import Blueprint

basedir = os.path.abspath(os.path.dirname(__file__))
# تعديل المسار ليشير مباشرة إلى مجلد الـ templates داخل موديول whatsapp_service
template_dir = os.path.abspath(os.path.join(basedir, '../templates'))

# تعريف الـ Blueprint الرئيسي مع تحديد مسار القوالب الصحيح
whatsapp_bp = Blueprint('whatsapp_service', __name__, template_folder=template_dir)

# استيراد الملفات الفرعية لربط المسارات (Routes) بالـ Blueprint
from . import webhook, dashboard, actions, api
