# admin_panel/routes.py
from flask import render_template, redirect, url_for, flash
from flask_login import login_required, logout_user
from core import db
from core.models.user import User
from core.models.supplier import Supplier
from datetime import datetime

# استيراد البلوبرنت والمحركات
from . import admin_bp
from .auth import login_view 
from .engines.supplier_engine import get_suppliers_by_filter # استدعاء المحرك هنا

# ==========================================
# 1. بوابة الولوج (The Login Gate)
# ==========================================
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    return login_view()

# ==========================================
# 2. غرفة القيادة (Dashboard)
# ==========================================
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        data = {
            'users_count': User.query.count(),
            'suppliers_count': Supplier.query.count(),
            'orders_count': 0, 
            'total_yer': db.session.query(db.func.sum(Supplier.balance_yer)).scalar() or 0.0,
            'total_sar': db.session.query(db.func.sum(Supplier.balance_sar)).scalar() or 0.0,
            'total_usd': db.session.query(db.func.sum(Supplier.balance_usd)).scalar() or 0.0,
            'now': datetime.now()
        }
        return render_template('admin/dashboard.html', **data)
    except Exception as e:
        return f"⚠️ خطأ في الرادار: {e}"

# ==========================================
# 3. إدارة العرض (Management Views)
# ==========================================
@admin_bp.route('/suppliers')
@login_required
def manage_suppliers():
    """هنا نعتمد على المحرك كلياً، ولن نحتاج لتعديل هذا المسار مستقبلاً"""
    # نطلب من المحرك آخر 10 موردين فقط للتحميل الأولي
    latest_suppliers = get_suppliers_by_filter(limit=10)
    
    # إحصائيات سريعة للواجهة
    stats = {
        'total': Supplier.query.count(),
        'active': Supplier.query.filter_by(status='active').count(),
        'sovereign': Supplier.query.filter_by(tier='سيادي').count()
    }
    
    return render_template('admin/manage_suppliers.html', 
                           suppliers=latest_suppliers, 
                           stats=stats)

# ==========================================
# 4. بروتوكول الخروج الآمن (Logout)
# ==========================================
@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("تم تسجيل الخروج. النظام في وضع الحماية.", "info")
    return redirect(url_for('admin.login'))
