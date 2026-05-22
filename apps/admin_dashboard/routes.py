# coding: utf-8
from flask import render_template, request
from flask_login import login_required
from apps.admin_dashboard import admin_dashboard_bp

@admin_dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard_home():
    # التحقق من نوع الطلب (AJAX)
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # تنفيذ منطق جلب البيانات
    # تأكد من أن هذه الدالة لا تسبب خطأ
    totals = {'total_yer': 0, 'total_sar': 0, 'total_usd': 0} 
    
    # إرجاع استجابة في جميع الحالات
    if is_ajax:
        return render_template('admin/dashboard_content.html', totals=totals)
    
    # هذا السطر يضمن دائماً وجود return حتى لو لم يكن الطلب AJAX
    return render_template('admin/admin_base.html')
