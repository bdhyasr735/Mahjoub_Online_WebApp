# coding: utf-8
# 📂 apps/orders/registry.py

from flask import Blueprint, render_template

# 1. إنشاء الـ Blueprint الخاص بالطلبات
orders_bp = Blueprint('orders_bp', __name__, template_folder='templates', url_prefix='/admin/orders')

# 2. إعدادات القائمة الجانبية (تظهر تلقائياً في الإدارة)
MODULE_NAME = 'إدارة الطلبات'
MODULE_ICON = 'fas fa-boxes'
SHOW_IN_SUPPLIER = False  # يظهر للإدارة فقط

# الروابط التي ستظهر في الشريط الجانبي تحت هذا القسم
LINKS = {
    'orders_bp.list_orders': 'عرض الطلبات',
}

# 3. مسارات الموديول (يمكنك وضعها هنا أو استيرادها من ملف routes.py منفصل)
@orders_bp.route('/')
def list_orders():
    # منطق عرض الطلبات هنا
    return render_template('admin/orders/list.html')

# 4. الدالة التي يتم استدعاؤها تلقائياً بواسطة apps/__init__.py
def register_module(app):
    app.register_blueprint(orders_bp)
    print("✅ [Module]: تم تفعيل موديول إدارة الطلبات بنجاح.")
