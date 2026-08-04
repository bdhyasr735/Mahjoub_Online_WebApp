# coding: utf-8
# 📂 apps/admin_orders/routes/__init__.py

from flask import Blueprint

# تعريف الـ Blueprint الرئيسي للموديول
admin_orders_bp = Blueprint(
    'admin_orders_bp',  # ✅ غير الاسم إلى 'admin_orders_bp' ليتطابق مع ما تستخدمه في registry.py
    __name__,
    template_folder='../templates',
    url_prefix='/admin/orders'
)

# ❌ احذف هذين السطرين نهائياً:
# from apps.admin_orders.routes import orders, actions

# ✅ بدلاً من ذلك، استورد الملفات الفرعية عند الحاجة (مثلاً داخل دوال الـ view)
# أو استوردها في نهاية الملف إذا كانت لا تسبب دائرة، لكن الأفضل استخدام Lazy Import داخل الدوال.
