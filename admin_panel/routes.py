from flask import Blueprint, render_template

# تعريف بوابة الإدارة
admin_bp = Blueprint('admin', __name__, 
                     template_folder='templates',
                     static_folder='static')

@admin_bp.route('/admin/login')
def login():
    return render_template('admin/login.html')

@admin_bp.route('/admin/dashboard')
def dashboard():
    return render_template('admin/dashboard.html')

@admin_bp.route('/admin/wallets')
def wallets():
    return render_template('admin/wallets.html')
