# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/__init__.py

from flask import Blueprint

# 1. تعريف البلوبرنت
admin_treasury_bp = Blueprint(
    'admin_treasury',
    __name__,
    template_folder='templates',
    static_folder='static'
)

# 2. استيراد مسارات المتحكم مباشرة (بدون try...except) 
# يجب أن يكون الاستيراد نسبياً وبدون إخفاء الأخطاء، لكي يظهر لك أي خطأ بوضوح في السجل إن وُجد.
from .routes import treasury_controller
