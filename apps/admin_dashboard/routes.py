# coding: utf-8
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
        # حساب إحصائية شركاء النجاح
        total_suppliers = Supplier.query.count()
        
        # استخدام أسماء الأعمدة المطابقة تماماً للموديل في wallet_db.py
        totals = db.session.query(
            func.sum(SupplierWallet.yer_total).label('total_yer'),
            func.sum(SupplierWallet.sar_total).label('total_sar'),
            func.sum(SupplierWallet.usd_total).label('total_usd')
        ).first()

        # تجهيز البيانات للقالب
        stats_data = {
            'total_yer': totals.total_yer or 0,
            'total_sar': totals.total_sar or 0,
            'total_usd': totals.total_usd or 0
        }
        
        return render_template('admin/dashboard_content.html', 
                               current_user=current_user, 
                               totals=stats_data,
                               total_suppliers=total_suppliers)
                               
    except Exception as e:
        return f"خطأ في تحميل مركز القيادة: {str(e)}", 500

@admin_dashboard.route('/settings', methods=['GET'])
@login_required
def system_settings():
    return render_template('admin/settings.html', current_user=current_user)

@admin_dashboard.route('/suppliers', methods=['GET'])
@login_required
def list_suppliers():
    suppliers = Supplier.query.all()
    return render_template('admin/suppliers.html', suppliers=suppliers)
