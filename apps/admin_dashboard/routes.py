# coding: utf-8
# 📊 لوحة التحكم الإدارية - منصة محجوب أونلاين 2026

from flask import Blueprint, render_template
from flask_login import login_required
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.utils.security import cipher_suite # استيراد الأداة الآمنة

# تعريف الـ Blueprint الخاص بلوحة التحكم مع تحديد مجلد القوالب المحلي
# هذا التعديل يحل مشكلة TemplateNotFound
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

@admin_dashboard.route('/admin/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    تحميل بيانات لوحة التحكم مع معالجة آمنة للقيم المشفرة والأعمدة
    """
    try:
        # 1. إحصائيات الموردين
        total_suppliers = Supplier.query.count()
        
        # 2. حساب الأرصدة 
        # تم استخدام دالة decrypt_to_float لفك التشفير أو التحويل الآمن
        wallets = SupplierWallet.query.all()
        
        # نستخدم الدالة الجديدة بدلاً من float() لتجنب الانهيار
        total_sar_balance = sum([cipher_suite.decrypt_to_float(w._sar_total) for w in wallets])
        total_yer_balance = sum([cipher_suite.decrypt_to_float(w._yer_total) for w in wallets])
        
        # إجمالي الرصيد للعرض في القالب
        total_balance = total_sar_balance + (total_yer_balance / 3.75) 
        
        # 3. آخر 5 عمليات
        recent_activities = WalletTransaction.query.order_by(
            WalletTransaction.created_at.desc()
        ).limit(5).all()
        
        # 4. التسويات المعلقة
        pending_settlements = WalletTransaction.query.filter_by(status='معلقة').count()

        # لاحظ: المسار 'admin/dashboard_content.html' سيتم البحث عنه داخل 
        # apps/admin_dashboard/templates/admin/dashboard_content.html
        return render_template(
            'admin/dashboard_content.html',
            total_suppliers=total_suppliers,
            total_balance=f"{total_balance:,.2f}",
            pending_settlements=pending_settlements,
            recent_activities=recent_activities
        )
        
    except Exception as e:
        # تسجيل الخطأ بالتفصيل في سجلات Railway للتشخيص
        print(f"❌ Error loading dashboard: {str(e)}")
        
        # رسالة واجهة المستخدم في حال فشل تحميل البيانات
        return """
        <div style="text-align:center; margin-top:50px; font-family:sans-serif;">
            <h2>حدث خطأ أثناء تحميل لوحة التحكم</h2>
            <p>يرجى التأكد من أن الأعمدة مشفرة بشكل صحيح في قاعدة البيانات.</p>
            <a href="/admin/dashboard" style="padding:10px; background:#632C8F; color:white; text-decoration:none; border-radius:5px;">حاول مجدداً</a>
        </div>
        """, 500
