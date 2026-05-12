from flask import Blueprint, render_template

# تعريف البلوبرنت الخاص بالإدارة
admin_bp = Blueprint('admin', __name__, template_folder='templates')

@admin_bp.route('/dashboard')
def dashboard():
    # استدعاء ملف المحتوى من المسار: templates/admin/dashboard_content.html
    return render_template('admin/dashboard_content.html')
