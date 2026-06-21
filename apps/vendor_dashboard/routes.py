# coding: utf-8
# 📂 apps/vendor_dashboard/routes.py

from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from apps import db
# استيراد الموديلات المطلوبة هنا عند الحاجة
# from apps.models.order_db import Order 

dashboard_bp = Blueprint('vendor_dashboard', __name__, template_folder='templates')

@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    """
    لوحة تحكم المورد السيادية:
    1. تتحقق من اكتمال البيانات (is_setup_complete).
    2. تمرر البيانات للمورد بأمان.
    """
    
    # التحقق من حالة المورد (هل أكمل ملفه الشخصي؟)
    # نستخدم getattr للتعامل بأمان في حال لم تكن الخاصية موجودة في الموديل
    is_ready = getattr(current_user, 'is_setup_complete', False)
    
    if not is_ready:
        # توجيه المورد لصفحة الإعداد إذا لم يكمل بياناته
        return redirect(url_for('vendors.setup_profile'))

    # جلب البيانات المطلوبة للوحة التحكم مع معالجة الأخطاء
    try:
        # جلب أحدث الطلبات (قم بفك التعليق وتعديل الموديل عند تجهيز جداول الطلبات)
        # recent_orders = Order.query.filter_by(supplier_id=current_user.id).order_by(Order.created_at.desc()).limit(5).all()
        recent_orders = [] 
        
        # إحصائيات المورد (يمكنك لاحقاً ربطها بدالة حسابية من الموديلات)
        supplier_stats = {
            'total_sales': "0.00",
            'pending_orders': 0
        }
        
    except Exception as e:
        # في حال حدوث أي خطأ في قاعدة البيانات، نعرض اللوحة فارغة بدلاً من انهيار النظام
        print(f"DEBUG: Dashboard Data Error: {e}")
        recent_orders = []
        supplier_stats = {'total_sales': "0.00", 'pending_orders': 0}

    return render_template(
        'vendor/dashboard.html', 
        recent_orders=recent_orders, 
        supplier_stats=supplier_stats
    )

@dashboard_bp.route('/settings')
@login_required
def settings():
    """صفحة إعدادات الحساب للمورد"""
    return "صفحة إعدادات المورد قيد التطوير - يمكنك إضافة النموذج الخاص بتحديث البيانات هنا"
