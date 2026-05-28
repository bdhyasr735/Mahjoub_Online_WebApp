# coding: utf-8
from flask import Blueprint

# تعريف البلوبرينت وتحديد مسار القوالب ليكون داخل المجلد الخاص به
add_supplier = Blueprint(
    'add_supplier', 
    __name__, 
    template_folder='templates'
)

# نقوم بعمل استيراد للمسارات هنا لضمان تفعيلها عند استدعاء البلوبرينت
from . import routes
