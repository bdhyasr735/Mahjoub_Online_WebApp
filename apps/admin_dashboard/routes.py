# coding: utf-8
# 📊 لوحة التحكم الإدارية - منصة محجوب أونلاين 2026

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from apps.extensions import db 
from sqlalchemy import func

# تعريف الـ Blueprint
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates',
    url_prefix='/admin'
)

@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    تحميل بيانات لوحة التحكم مع تحصين كامل ضد انهيار قاعدة البيانات
    """
    # 1. الاستيراد المحلي (Lazy Import) - نكسر الحلقة الدائرية بوضعه هنا
    from apps.models.supplier_db import Supplier
    from apps.models.wallet_db import SupplierWallet, WalletTransaction
    
    # 2. قيم افتراضية لضمان عدم انهيار القالب (Template) في حال كانت القاعدة فارغة
    stats = {
        'total_suppliers': 0,
        'total_balance': "0.00",
        'pending_settlements': 0,
        'recent_activities': []
    }

    try:
        # إحصائيات الموردين
        stats['total_suppliers'] = Supplier.query.count() or 0
        
        # حساب الأرصدة (باستخدام تحصين لضمان عدم وجود قيمة None)
        sar_sum = db.session.query(func.sum(SupplierWallet.sar_total)).scalar() or 0
        yer_sum = db.session.query(func.sum(SupplierWallet.yer_total)).scalar() or 0
        
        # معادلة تحويل العملة الذكية
        total_balance = float(sar_sum) + (float(yer_sum) / 3.75)
        stats['total_balance'] = f"{total_balance:,.2f}"

        # جلب آخر 5 عمليات مع ترتيب عكسي دقيق
        stats['recent_activities'] = WalletTransaction.query.order_by(
            WalletTransaction.id.desc()
        ).limit(5).all()
        
        # التسويات المعلقة
        stats['pending_settlements'] = WalletTransaction.query.filter_by(status='معلقة').count() or 0

        # إرجاع الصفحة مع تمرير البيانات
        return render_template('admin/dashboard_content.html', **stats)
        
    except Exception as e:
        # 🛡️ الحماية من الانهيار: في حال حدث أي خطأ تقني، سجل الخطأ وأظهر اللوحة فارغة
        print(f"❌ Critical Dashboard Error: {str(e)}")
        return render_template('admin/dashboard_content.html', **stats)

# تأكد أنك ستضيف مسارات أخرى هنا بنفس الهيكلية (مثلاً route للموردين)
