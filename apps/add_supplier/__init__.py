# coding: utf-8
from flask import Blueprint

# تعريف البلوبرينت (Blueprint) الخاص بتطبيق إضافة الموردين
# ملاحظة: تم اختيار 'admin_suppliers' ليتوافق مع استدعاءات الـ URL في المنظومة
admin_suppliers = Blueprint(
    'admin_suppliers', 
    __name__,
    template_folder='templates',
    static_folder='static'
)

# استيراد المسارات (Routes) لربطها بالبلوبرينت
# يتم الاستيراد في الأسفل لتجنب مشكلة الاستيراد الدائري (Circular Import)
from . import routes
