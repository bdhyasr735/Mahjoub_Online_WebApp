from flask import Blueprint

# إنشاء البلوبرنت الخاص بقطاع الموردين (The Supplier Sector)
# تم تحديد مجلد القوالب 'templates' لضمان قراءة التصاميم السيادية
supplier_bp = Blueprint(
    'supplier_panel', 
    __name__, 
    template_folder='templates',
    static_folder='static'
)

# ملاحظة حاسمة: يجب استيراد routes في الأسفل لتجنب مشكلة (Circular Import)
# هذا الاستيراد هو الذي يربط المسارات (الدخول، الداشبورد، الترسانة) بالبلوبرنت
from . import routes
