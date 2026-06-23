# coding: utf-8
# 📂 apps/admin_dashboard/routes.py - لوحة تحكم الإدارة المركزية (مُحدث بالكامل)

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
import traceback

# استيراد النماذج
from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier

admin_dashboard = Blueprint('admin_dashboard', __name__, template_folder='templates')

@admin_dashboard.route('/dashboard')
@login_required
def dashboard():
    """
    لوحة تحكم القيادة المركزية للمدير
    """
    try:
        # 1. حماية سيادية: التحقق من الصلاحية
        if not isinstance(current_user, AdminUser):
            flash("هذه المنطقة مخصصة للمدراء فقط.", "danger")
            return redirect(url_for('auth_portal.login'))

        # 2. جلب البيانات المطلوبة في القالب
        # جلب عدد الموردين
        total_suppliers = Supplier.query.count()
        
        # تعريف المتغيرات المالية (تم تعيينها كـ 0.0 لتجنب الأخطاء عند عدم وجود بيانات)
        # يمكنك استبدال هذه الأصفار باستعلامات من قاعدة بيانات العمليات المالية إذا توفرت
        total_balance_sar = 0.0
        total_balance_yer = 0.0
        total_balance_usd = 0.0
        recent_transactions = [] # هنا يمكنك جلب العمليات الأخيرة: Transaction.query.order_by(...).limit(5).all()

        # 3. إرسال المتغيرات للقالب (تطابق القالب تماماً)
        return render_template(
            'admin/dashboard.html',
            total_suppliers=total_suppliers,
            total_balance_sar=total_balance_sar,
            total_balance_yer=total_balance_yer,
            total_balance_usd=total_balance_usd,
            recent_transactions=recent_transactions
        )
        
    except Exception as e:
        # 💡 طباعة الخطأ الحقيقي بالتفصيل في الـ Logs لتسهيل التصحيح
        print(f"🚨 [CRITICAL ERROR] Dashboard failed: {traceback.format_exc()}")
        return f"حدث خطأ فني أثناء تحميل لوحة التحكم: {str(e)}", 500

@admin_dashboard.route('/settings')
@login_required
def settings():
    if not isinstance(current_user, AdminUser):
        return redirect(url_for('auth_portal.login'))
    return "صفحة إعدادات النظام قيد التطوير"

@admin_dashboard.route('/suppliers')
@login_required
def manage_suppliers():
    """عرض قائمة الموردين للمدير"""
    if not isinstance(current_user, AdminUser):
        return redirect(url_for('auth_portal.login'))
        
    suppliers = Supplier.query.all()
    return render_template('admin/suppliers.html', suppliers=suppliers)
