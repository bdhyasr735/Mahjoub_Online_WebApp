# 📂 apps/admin_dashboard/routes.py

from flask import Blueprint, render_template
from flask_login import login_required

# 1. إنشاء الـ Blueprint
# الاسم 'admin_dashboard' هو الذي سيتم استخدامه في url_for('admin_dashboard.dashboard')
admin_dashboard = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates'
)

# 2. تعريف المسار (Route)
@admin_dashboard.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    عرض لوحة تحكم النظام الرئيسية.
    هنا نقوم بتمرير المتغيرات المطلوبة في قالب dashboard.html
    """
    
    # يمكنك لاحقاً إضافة المنطق لجلب البيانات الحقيقية من قاعدة البيانات
    context = {
        "total_suppliers": 0,           # استبدل بـ استعلام قاعدة البيانات
        "total_balance_sar": 0.00,      # استبدل بـ استعلام قاعدة البيانات
        "total_balance_yer": 0.00,      # استبدل بـ استعلام قاعدة البيانات
        "total_balance_usd": 0.00,      # استبدل بـ استعلام قاعدة البيانات
        "recent_transactions": []       # قائمة العمليات الأخيرة
    }
    
    # القالب المسار الخاص به بالنسبة للـ Blueprint هو 'admin/dashboard.html'
    return render_template('admin/dashboard.html', **context)

# إذا احتجت مسارات إضافية، أضفها هنا بنفس النمط:
# @admin_dashboard.route('/reports')
# @login_required
# def reports():
#     return render_template('admin/reports.html')
