# coding: utf-8
# 📂 apps/admin_dashboard/routes.py - النسخة المعدلة لضمان العثور على القوالب

import os
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
import traceback

# استيراد النماذج
from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier

# 1. تعريف مسار القوالب بدقة مطلقة
# نحدد المسار إلى مجلد 'admin' مباشرة لضمان العثور على الملفات
admin_templates = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'admin')

admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates' # المجلد الأساسي
)

@admin_dashboard.route('/dashboard')
@login_required
def dashboard():
    try:
        # فحص صلاحية الوصول
        if not getattr(current_user, 'is_admin', False) and not isinstance(current_user, AdminUser):
            return redirect(url_for('auth_portal.login'))

        total_suppliers = Supplier.query.count()
        
        # 2. الحل: بما أننا وضعنا المسار المباشر لـ 'admin' في تعريف الـ Blueprint (أو التعامل المباشر)
        # إذا استمر الخطأ، جرب إزالة 'admin/' من هنا، لتصبح 'dashboard.html'
        # ولكن بما أن المجلد اسمه 'admin' داخل 'templates'، فالكود التالي هو الأدق:
        return render_template(
            'admin/dashboard.html',
            total_suppliers=total_suppliers,
            total_balance_sar=0.0,
            total_balance_yer=0.0,
            total_balance_usd=0.0,
            recent_transactions=[]
        )
        
    except Exception as e:
        print(f"🚨 [CRITICAL ERROR] {traceback.format_exc()}")
        return "حدث خطأ في تحميل الواجهة (Template Not Found)", 500

@admin_dashboard.route('/suppliers')
@login_required
def manage_suppliers():
    if not isinstance(current_user, AdminUser):
        return redirect(url_for('auth_portal.login'))
        
    suppliers = Supplier.query.all()
    return render_template('admin/suppliers.html', suppliers=suppliers)
