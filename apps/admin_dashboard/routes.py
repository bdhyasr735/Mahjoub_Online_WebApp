# coding: utf-8
# 📊 لوحة التحكم الإدارية - منصة محجوب أونلاين 2026

from flask import Blueprint, render_template
from flask_login import login_required
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet, WalletTransaction

# تعريف الـ Blueprint الخاص بلوحة التحكم
admin_dashboard = Blueprint('admin_dashboard', __name__)

@admin_dashboard.route('/admin/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    تحميل بيانات لوحة التحكم.
    تم تنظيم الاستيرادات لتكون في الأعلى لضمان سرعة الاستجابة.
    """
    try:
        # 1. إحصائيات سريعة
        total_suppliers = Supplier.query.count()
        
        # 2. حساب الأرصدة (استخدام الموديل مباشرة بكفاءة)
        wallets = SupplierWallet.query.all()
        total_sar_balance = sum([w.sar_total or 0 for w in wallets])
        total_yer_balance = sum([w.yer_total or 0 for w in wallets])
        
        # 3. آخر 5 عمليات
        recent_activities = WalletTransaction.query.order_by(
            WalletTransaction.created_at.desc()
        ).limit(5).all()
        
        # 4. التسويات المعلقة
        pending_settlements = WalletTransaction.query.filter_by(status='معلقة').count()

        return render_template(
            'admin/dashboard_content.html',
            total_suppliers=total_suppliers,
            total_sar_balance=total_sar_balance,
            total_yer_balance=total_yer_balance,
            pending_settlements=pending_settlements,
            recent_activities=recent_activities
        )
        
    except Exception as e:
        # تسجيل الخطأ في الـ Logs الخاصة بـ Railway
        print(f"❌ Error loading dashboard: {str(e)}")
        return "حدث خطأ أثناء تحميل لوحة التحكم، يرجى مراجعة سجلات النظام.", 500
