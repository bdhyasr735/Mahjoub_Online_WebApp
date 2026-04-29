from flask import Blueprint
from .auth_controller import AdminAuthController

# تعريف البلوبرينت الخاص بالإدارة
# تم تحديد template_folder لضمان التعرف على مسار admin_panel/templates
admin_bp = Blueprint(
    'admin_panel', 
    __name__, 
    template_folder='templates'
)

# إنشاء نسخة من المتحكم لإدارة منطق الدخول والعمليات
auth_controller = AdminAuthController()

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """مسار تسجيل دخول الإدارة - يربط مع admin_panel/login.html"""
    return auth_controller.login_logic()

@admin_bp.route('/dashboard')
def admin_dashboard():
    """لوحة التحكم المركزية للمنصة"""
    return auth_controller.dashboard_logic()

@admin_bp.route('/suppliers-management')
def manage_suppliers():
    """إدارة شركاء النجاح (الموردين) والرقابة على سلاسل التوريد"""
    return auth_controller.suppliers_logic()

@admin_bp.route('/logout')
def logout():
    """تسجيل الخروج الآمن من نظام الإدارة"""
    return auth_controller.logout_logic()
