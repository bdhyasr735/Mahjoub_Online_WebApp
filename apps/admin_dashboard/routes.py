from flask import Blueprint, render_template

admin_dashboard = Blueprint('admin_dashboard', __name__, template_folder='templates')

@admin_dashboard.route('/')
@admin_dashboard.route('/dashboard')
def dashboard():
    # هنا نستدعي ملف المحتوى الذي سيرث الهيكل تلقائياً
    return render_template('admin/dashboard_content.html')
