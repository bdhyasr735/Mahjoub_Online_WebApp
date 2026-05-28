# coding: utf-8
# 📊 لوحة التحكم الإدارية - منصة محجوب أونلاين 2026

from flask import Blueprint, render_template, request
from flask_login import login_required
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.utils.security import cipher_suite

# تعريف الـ Blueprint
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

@admin_dashboard.route('/admin/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    تحميل بيانات لوحة التحكم مع تأمين الاستعلامات
    """
    try:
        # 1. إحصائيات الموردين
        total_suppliers = Supplier.query.count()
        
        # 2. حساب الأرصدة
        wallets = SupplierWallet.query.all()
        total_sar_balance = sum([w.sar_total for w in wallets])
        total_yer_balance = sum([w.yer_total for w in wallets])
        total_balance = total_sar_balance + (total_yer_balance / 3.75) 
        
        # 3. آخر 5 عمليات (ترتيب آمن)
        # نستخدم قائمة فارغة كـ fallback إذا فشل الاستعلام بسبب نقص أعمدة
        try:
            recent_activities = WalletTransaction.query.order_by(
                WalletTransaction.created_at.desc()
            ).limit(5).all()
        except:
            recent_activities = []
        
        # 4. التسويات المعلقة (معالجة استثناء في حال عدم وجود عمود status)
        try:
            pending_settlements = WalletTransaction.query.filter_by(status='معلقة').count()
        except:
            pending_settlements = 0

        return render_template(
            'admin/dashboard_content.html',
            total_suppliers=total_suppliers,
            total_balance=f"{total_balance:,.2f}",
            pending_settlements=pending_settlements,
            recent_activities=recent_activities
        )
        
    except Exception as e:
        print(f"❌ Error loading dashboard: {str(e)}")
        
        return """
        <div style="text-align:center; margin-top:50px; font-family:sans-serif; direction:rtl;">
            <h2>عذراً، حدث خطأ تقني في عرض البيانات</h2>
            <p>يتم العمل على مزامنة هيكل قاعدة البيانات، يرجى المحاولة بعد قليل.</p>
            <a href="/admin/dashboard" style="padding:10px; background:#632C8F; color:white; text-decoration:none; border-radius:5px;">حاول مجدداً</a>
        </div>
        """, 500
