# -*- coding: utf-8 -*-
# 📂 apps/suppliers_auth_portal/routes.py

from flask import render_template, request
from apps.suppliers_auth_portal import suppliers_bp
from apps.suppliers_auth_portal.auth_register import register_supplier_logic

@suppliers_bp.route('/register', methods=['GET', 'POST'])
def register():
    """مسار عرض نموذج تسجيل المورد الجديد أو معالجة طلب التسجيل"""
    if request.method == 'POST':
        return register_supplier_logic()
    return render_template('suppliers_auth_portal/register.html')
