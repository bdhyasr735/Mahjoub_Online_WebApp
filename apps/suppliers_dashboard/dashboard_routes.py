# coding: utf-8
# 📂 apps/suppliers_dashboard/routes/dashboard_routes.py

from flask import Blueprint, render_template, session, redirect
from flask_login import login_required, current_user

from apps.models import db, Supplier, SupplierWallet

suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    template_folder='templates'
)


@suppliers_dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    try:
        # ✅ عرض رسالة بسيطة للتأكد من أن الدالة تعمل
        return "<h1 style='text-align:center;margin-top:50px;color:#2d0b36;'>✅ لوحة التحكم تعمل</h1><p style='text-align:center;'>المستخدم: " + str(current_user.id) + "</p>"
        
    except Exception as e:
        return f"❌ خطأ: {str(e)}", 500
