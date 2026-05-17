# coding: utf-8
# 🔑 مسارات محرك الموردين المعزول - محجوب أونلاين 2026

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
import jinja2

# استيراد البلوبرينت الصحيح المعمد في الـ __init__
from . import admin_suppliers

@admin_suppliers.route('/add', methods=['GET', 'POST'])
@login_required  # حماية النفاذ السيادي
def add_supplier():
    """تعميد وإضافة مورد جديد للمنصة"""
    if request.method == 'POST':
        # هنا ستكون معالجة البيانات وإضافتها لقاعدة البيانات لاحقاً
        flash('تم تعميد المورد بنجاح في النظام الرقمي.', 'success')
        return redirect(url_for('admin_dashboard.dashboard_home'))
        
    # محاولة رندرة القالب من المجلد الفرعي، وإذا تعذر يقرأه مباشرة منعا للـ 500
    try:
        return render_template('admin/add_supplier.html', owner=current_user)
    except jinja2.exceptions.TemplateNotFound:
        return render_template('add_supplier.html', owner=current_user)
