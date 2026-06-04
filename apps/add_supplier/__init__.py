from flask import Blueprint

# تعريف الـ Blueprint الخاص بهذا المجلد
# 'add_supplier' هو اسم الـ blueprint
# __name__ يحدد مسار الملف
# template_folder يحدد أين توجد ملفات HTML الخاصة بهذا القسم
add_supplier_bp = Blueprint(
    'add_supplier', 
    __name__, 
    template_folder='templates',
    url_prefix='/add_supplier'
)

# استيراد المسارات لربطها بالـ blueprint
from . import routes
