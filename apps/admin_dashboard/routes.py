# coding: utf-8
# 🖥️ مستند مسارات مركز القيادة - منصة محجوب أونلاين 2026

from flask import render_template
from flask_login import login_required, current_user
from . import admin_dashboard
from apps import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet
from sqlalchemy import func

@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard_home():
    try:
        # حساب إحصائية شركاء النجاح بأمان
        total_suppliers = 0
        try:
            total_suppliers = Supplier.query.count()
        except Exception:
            db.session.rollback()

        # استخدام أسماء الأعمدة المطابقة تماماً للموديل في wallet_db.py
        stats_data = {'total_yer': 0, 'total_sar': 0, 'total_usd': 0}
        try:
            totals = db.session.query(
                func.sum(SupplierWallet.yer_total).label('total_yer'),
                func.sum(SupplierWallet.sar_total).label('total_sar'),
                func.sum(SupplierWallet.usd_total).label('total_usd')
            ).first()
            
            if totals:
                stats_data['total_yer'] = totals.total_yer or 0
                stats_data['total_sar'] = totals.total_sar or 0
                stats_data['total_usd'] = totals.total_usd or 0
        except Exception:
            db.session.rollback()

        # 👑 تمرير البيانات مع حماية الـ current_user من أي استدعاء مكسور في الـ Template
        return render_template('admin/dashboard_content.html', 
                               current_user=current_user, 
                               totals=stats_data,
                               total_suppliers=total_suppliers)
                               
    except Exception as e:
        db.session.rollback()
        return render_template('admin/admin_base.html', 
                               current_user=current_user, 
                               totals={'total_yer': 0, 'total_sar': 0, 'total_usd': 0},
                               total_suppliers=0,
                               error_msg=str(e))

@admin_dashboard.route('/settings', methods=['GET'])
@login_required
def system_settings():
    return render_template('admin/settings.html', current_user=current_user)

@admin_dashboard.route('/suppliers', methods=['GET'])
@login_required
def list_suppliers():
    try:
        suppliers = Supplier.query.all()
    except Exception:
        db.session.rollback()
        suppliers = []
    return render_template('admin/suppliers.html', suppliers=suppliers)
