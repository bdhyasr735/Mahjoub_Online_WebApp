from flask import Blueprint, render_template
from flask_login import login_required
from .auth_controller import AdminAuthController

# تعريف البلوبرينت مع تحديد مسار القوالب بدقة
admin_bp = Blueprint('admin_panel', __name__, template_folder='templates')

# إنشاء نسخة من المتحكم لضمان استمرارية الجلسة والمنطق البرمجي
auth_controller = AdminAuthController()

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    # تأكد أن الدالة في Controller ترجع render_template أو redirect
    return auth_controller.login_logic()

@admin_bp.route('/dashboard')
@login_required
def admin_dashboard():
    return auth_controller.dashboard_logic()

@admin_bp.route('/suppliers-management')
@login_required
def manage_suppliers():
    return auth_controller.suppliers_logic()

@admin_bp.route('/product-review')
@login_required
def sync_now():
    return auth_controller.sync_logic()

@admin_bp.route('/wallets')
@login_required
def wallets():
    return auth_controller.wallets_logic()

@admin_bp.route('/logout')
@login_required
def logout():
    return auth_controller.logout_logic()
