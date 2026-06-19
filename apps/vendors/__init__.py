from flask import Blueprint

# إنشاء الـ Blueprint الخاص بالموردين
vendors_bp = Blueprint('vendors', __name__, template_folder='templates')

# استيراد الـ routes لكي يتم تسجيلها عند تشغيل التطبيق
from . import routes
