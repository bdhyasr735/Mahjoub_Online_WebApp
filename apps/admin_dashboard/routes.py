# coding: utf-8
# 📂 apps/admin_dashboard/routes.py - لوحة التحكم السيادية (مُحَصّنة)

from flask import Blueprint, render_template, abort, session
from flask_login import login_required, current_user
from apps.extensions import db
from sqlalchemy import func, exc
from datetime import datetime

# استيراد النماذج
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet, WalletTransaction

admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

@admin_dashboard.before_request
@login_required
def make_session_permanent():
    session.permanent = True
    session.modified = True 

@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # 🛡️ حماية سيادية
    if current_user.role not in ['Owner', 'Admin']:
        abort(403)

    try:
        # إحصائيات الموردين (دفاعي)
        total_suppliers = Supplier.query.count()
        
        # إحصائيات مالية دفاعية (تتجنب الخطأ في حال عدم وجود جدول أو بيانات)
        try:
            total_sar = db.session.query(func.sum(SupplierWallet.sar_total)).scalar() or 0.0
            total_yer = db.session.query(func.sum(SupplierWallet.yer_total)).scalar() or 0.0
            recent_transactions = WalletTransaction.query.order_by(WalletTransaction.id.desc()).limit(10).all()
        except Exception:
            total_sar, total_yer, recent_transactions = 0.0, 0.0, []

        context = {
            'total_suppliers': total_suppliers,
            'total_balance_sar': float(total_sar),
            'total_balance_yer': float(total_yer),
            'recent_transactions': recent_transactions,
            'now': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user_name': current_user.username,
            'store_name': 'محجوب أونلاين'
        }
        
        return render_template('admin/dashboard_content.html', **context)
        
    except Exception as e:
        # حماية ضد انهيار الصفحة
        return f"🚨 خطأ تقني في استدعاء قاعدة البيانات: {str(e)}", 500

@admin_dashboard.route('/system_logs', methods=['GET'])
@login_required
def system_logs():
    if current_user.role != 'Owner':
        abort(403)
    return "سجل الأحداث السيادي - قيد التطوير"
