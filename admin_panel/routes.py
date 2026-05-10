# admin_panel/routes.py
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, logout_user
from core import db
from core.models.user import User
from core.models.supplier import Supplier
from datetime import datetime
from . import admin_bp

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """غرفة القيادة: عرض إحصائيات الترسانة المالية والعددية"""
    # جلب إحصائيات المحفظة الثلاثية من الكور
    stats = {
        'users': User.query.count(),
        'suppliers': Supplier.query.count(),
        'yer': db.session.query(db.func.sum(Supplier.balance_yer)).scalar() or 0,
        'sar': db.session.query(db.func.sum(Supplier.balance_sar)).scalar() or 0,
        'usd': db.session.query(db.func.sum(Supplier.balance_usd)).scalar() or 0,
        'time': datetime.now()
    }
    return render_template('admin/dashboard.html', **stats)

@admin_bp.route('/logout')
@login_required
def logout():
    """بروتوكول الخروج الآمن"""
    logout_user()
    flash("تم تأمين الخروج بنجاح.", "info")
    return redirect(url_for('admin.login'))
