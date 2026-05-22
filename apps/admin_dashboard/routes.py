# coding: utf-8
from flask import render_template
from flask_login import login_required
from . import admin_dashboard_bp

@admin_dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard_home():
    # استعلام مبسط لتجنب أخطاء الأعمدة المحذوفة
    return render_template('admin/dashboard_content.html', totals=None)

# هذا هو المسار الذي يبحث عنه النظام ولا يجده (أضفه الآن)
@admin_dashboard_bp.route('/suppliers', methods=['GET'])
@login_required
def list_suppliers():
    # سنقوم بربطه بقائمة الموردين لاحقاً
    return render_template('admin/suppliers_list.html')
