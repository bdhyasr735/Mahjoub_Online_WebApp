# coding: utf-8
# 📂 apps/suppliers_dashboard/dashboard_routes.py

from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from datetime import datetime, timedelta
import traceback

from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.supplier_staff_db import SupplierStaff
from apps.models.wallet_db import SupplierWallet

# ✅ تعريف الـ Blueprint
suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    template_folder='templates'
)


def get_supplier_context():
    """جلب بيانات المورد والمحفظة"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff', 'supplier_staff']:
            return None

        if user_type in ['staff', 'supplier_staff']:
            supplier_id = getattr(current_user, 'supplier_id', None)
        else:
            supplier_id = getattr(current_user, 'id', None)

        if not supplier_id:
            return None

        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            return None

        wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
        supplier.wallet = wallet

        return supplier

    except Exception as e:
        print(f"❌ خطأ في get_supplier_context: {e}")
        return None


@suppliers_dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """لوحة تحكم المورد"""
    try:
        supplier = get_supplier_context()
        if not supplier:
            flash('❌ يرجى تسجيل الدخول أولاً', 'danger')
            # ✅ العودة إلى بوابة تسجيل الدخول
            return redirect(url_for('auth_login.login'))

        # ✅ عرض لوحة التحكم
        return render_template(
            'suppliers/dashboard.html',
            supplier=supplier,
            wallet=supplier.wallet
        )

    except Exception as e:
        print(f"❌ خطأ في dashboard: {e}")
        flash('❌ حدث خطأ تقني في عرض لوحة التحكم', 'danger')
        return redirect(url_for('auth_login.login'))
