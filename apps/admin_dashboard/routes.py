# coding: utf-8
# 📂 apps/admin_dashboard/routes.py - لوحة التحكم السيادية (مُحدث بالبيانات الشخصية)

from flask import Blueprint, render_template, abort, session
from flask_login import login_required, current_user
from apps.extensions import db
from sqlalchemy import func
from datetime import datetime

# استيراد النماذج (Models)
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
    # تفعيل خمول الجلسة (15 دقيقة) لضمان الأمن السيادي
    session.permanent = True
    session.modified = True 

@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # 🛡️ حماية سيادية: لا يسمح بالدخول إلا لـ Owner أو Admin
    if current_user.role not in ['Owner', 'Admin']:
        abort(403)

    try:
        # استخراج الإحصائيات المالية
        total_sar = db.session.query(func.sum(SupplierWallet.sar_total)).scalar() or 0.0
        total_yer = db.session.query(func.sum(SupplierWallet.yer_total)).scalar() or 0.0
        
        # 🔑 استدعاء بيانات المستخدم والمتجر 
        # نستخدم username لأن هذا ما هو معرف فعلياً في جدول admin_users
        user_name = current_user.username if current_user.is_authenticated else 'المسؤول'
        store_name = 'محجوب أونلاين' # اسم ثابت للمتجر كما هو مطلوب
        
        # تجميع البيانات للوحة التحكم
        context = {
            'total_suppliers': Supplier.query.count(),
            'total_balance_sar': float(total_sar),
            'total_balance_yer': float(total_yer),
            'recent_transactions': WalletTransaction.query.order_by(WalletTransaction.id.desc()).limit(10).all(),
            'now': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'user_name': user_name,      # إرسال الاسم للقالب
            'store_name': store_name     # إرسال اسم المتجر للقالب
        }
        
        # تقديم القالب
        return render_template('admin/dashboard_content.html', **context)
        
    except Exception as e:
        # 🔐 حماية عند حدوث خطأ
        return f"🚨 خطأ تقني في استدعاء قاعدة البيانات: {str(e)}", 500

# إضافات مستقبلية للتحكم السيادي
@admin_dashboard.route('/system_logs', methods=['GET'])
@login_required
def system_logs():
    if current_user.role != 'Owner': # صلاحية خاصة للمالك فقط
        abort(403)
    return "سجل الأحداث السيادي - قيد التطوير"
