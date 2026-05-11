# admin_panel/__init__.py
from flask import Blueprint

# 1. تعريف البلوبرنت
admin_bp = Blueprint(
    'admin', 
    __name__, 
    template_folder='templates', 
    static_folder='static', 
    url_prefix='/admin'
)

# 2. استيراد الملفات لربطها بالبلوبرنت (مرة واحدة فقط!)
# ملاحظة: لا تستورد هذه الملفات في أي مكان آخر خارج هذا الملف
from . import auth
from . import routes
from . import add_supplier_routes
from . import supplier_service_routes
from . import staff_routes
