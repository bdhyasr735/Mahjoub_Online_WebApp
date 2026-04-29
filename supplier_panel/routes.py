from flask import Blueprint
from flask_login import login_required
# الربط مع ملف المنطق البرمجي الخاص بك
from .auth_logic import SupplierController 

# تعريف البلوبرينت الخاص بالموردين مع تحديد مجلد القوالب
supplier_bp = Blueprint('supplier_panel', __name__, template_folder='templates')

# إنشاء نسخة من المتحكم لضمان توافق الدوال
supplier_controller = SupplierController()

# --- مسارات بوابة دخول الموردين (شركاء النجاح) ---

@supplier_bp.route('/login', methods=['GET', 'POST'])
def supplier_login():
    """بوابة دخول الموردين - المرحلة الأولى"""
    return supplier_controller.login_logic()

@supplier_bp.route('/logout')
@login_required
def logout():
    """تسجيل خروج المورد بأمان"""
    return supplier_controller.logout_logic()

# --- مسارات إدارة السوق الذكي للمورد ---

@supplier_bp.route('/dashboard')
@login_required
def supplier_dashboard():
    """لوحة التحكم الخاصة بالمورد لمتابعة الأداء"""
    return supplier_controller.dashboard_logic()

@supplier_bp.route('/my-products')
@login_required
def manage_products():
    """إدارة مخزون ومنتجات المورد"""
    return supplier_controller.products_logic()

@supplier_bp.route('/orders')
@login_required
def view_orders():
    """متابعة طلبات العملاء الواردة"""
    return supplier_controller.orders_logic()

@supplier_bp.route('/account-settings')
@login_required
def settings():
    """تحديث بيانات الحساب وربط الـ Webhooks التقنية"""
    return supplier_controller.settings_logic()
