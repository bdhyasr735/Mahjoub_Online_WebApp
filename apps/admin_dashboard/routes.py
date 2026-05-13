from flask import render_template
from . import admin_dashboard 

@admin_dashboard.route('/')
@admin_dashboard.route('/dashboard')
def dashboard():
    # تعديل المسار ليتطابق مع مكان الملف الفعلي الذي ذكرته
    # Flask يبدأ البحث من داخل مجلد templates المعرف في __init__
    return render_template('admin/dashboard_content.html')

@admin_dashboard.route('/suppliers/list')
def list_suppliers():
    # تأكد أن هذا الملف موجود أيضاً في نفس المجلد الفرعي admin
    return render_template('admin/list_suppliers.html')
