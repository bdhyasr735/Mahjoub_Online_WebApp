# -*- coding: utf-8 -*-
# 📂 apps/admin_treasury/routes/__init__.py
"""
حزمة المتحكمات لموديول الرقابة المالية والخزينة المركزية
مشروع Mahjoub Online WebApp
"""

from flask import render_template
from flask_login import login_required
from apps.admin_treasury import admin_treasury_bp

@admin_treasury_bp.route('/', methods=['GET'])
@login_required
def treasury_index():
    """
    الصفحة الرئيسية للرقابة المالية والخزينة المركزية
    """
    kpi = {
        "total_treasury_balance": 0.0,
        "currency": "ريال يمني"
    }
    return render_template('admin/admin_treasury.html', kpi=kpi)
