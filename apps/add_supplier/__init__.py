# apps/add_supplier/__init__.py
# coding: utf-8

from flask import Blueprint

# تعريف البلوبرينت بشكل مستقل تماماً
# تمت إزالة تخصيص المجلد الفرعي للقوالب لكي يقرأ Flask تلقائياً من المجلد الرئيسي الموحد
admin_suppliers = Blueprint(
    'admin_suppliers',
    __name__,
    url_prefix='/admin/suppliers'
)

# الاستدعاء المتأخر للمسارات في نهاية الملف لكسر حلقة الاستيراد الدائري (Circular Import)
from apps.add_supplier import routes
