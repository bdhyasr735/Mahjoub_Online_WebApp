# coding: utf-8
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from apps.extensions import db  # التصحيح هنا لضمان استخدام الكائن المركزي المستقر والموحد للمنصة 
from apps.models.admin_db import AdminUser
from apps.models.supplier_db import Supplier  # التعديل الهيكلي الصحيح لمنع الـ ImportError ✅

# تعريف الـ Blueprint الخاص بلوحة التحكم الإدارية
admin_dashboard = Blueprint('admin_dashboard', __name__, template_folder='templates')

# تم إزالة /admin/ الزائدة ليتطابق التوجيه تماماً مع المتصفح وينهي خطأ الـ 404 المتكرر 🚀
@admin_dashboard.route('/', methods=['GET'])
@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # التحقق من صلاحيات المسؤول لضمان أمان السيادة المطلقة
    if not getattr(current_user, 'is_admin', False):
        flash('غير مسموح لك بالدخول إلى هذه المنطقة الأمنية.', 'danger')
        return redirect(url_for('auth_portal.login'))

    try:
        # حساب المؤشرات الحيوية رقمياً من قواعد البيانات مباشرة
        total_suppliers = Supplier.query.count()
    except Exception as e:
        total_suppliers = 0

    # بيانات تجريبية مؤقتة لسجل العمليات والنشاطات الإدارية حتى يكتمل ربط المحافظ
    recent_activities = [
        {
            "id": 1024,
            "user": "المؤسس علي",
            "type": "تحديث نظام",
            "amount": 0,
            "date": "2026-05-23 17:30",
            "status": "مكتمل"
        },
        {
            "id": 1023,
            "user": "مورد معتمد",
            "type": "تسوية مالية محفظة",
            "amount": 250,
            "date": "2026-05-23 16:15",
            "status": "معلق"
        }
    ]

    # إجمالي الأرصدة الافتراضية بانتظام موديول المحافظ
    total_balance = "0.00"
    pending_settlements = 1

    # استدعاء قالب العرض وتمرير كافة البيانات الديناميكية له
    return render_template(
        'admin/dashboard_content.html',
        total_suppliers=total_suppliers,
        total_balance=total_balance,
        pending_settlements=pending_settlements,
        recent_activities=recent_activities
    )
