from flask import Blueprint, render_template
from flask_login import login_required, current_user
# استيراد محركات المنطق (Logic Engines)
from .auth import login_view 
from .suppliers_logic import SupplierLogic
from .utils import admin_only # ديكوريتور سيادي لحماية الروابط

admin_bp = Blueprint('admin', __name__, template_folder='templates')

# ==========================================
# 1. بوابة الدخول والخروج (Security Gate)
# ==========================================
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    return login_view()

@admin_bp.route('/logout')
@login_required
def logout():
    from flask_login import logout_user
    logout_user()
    return redirect(url_for('admin.login'))

# ==========================================
# 2. غرفة القيادة المركزية (Main Dashboard)
# ==========================================
@admin_bp.route('/dashboard')
@login_required
@admin_only # لا يدخل هنا إلا من رتبته 'admin'
def dashboard():
    return render_template('admin/dashboard.html', user=current_user)

# ==========================================
# 3. إدارة ترسانة الموردين (Suppliers Management)
# ==========================================
@admin_bp.route('/suppliers')
@login_required
def manage_suppliers():
    suppliers = SupplierLogic.get_all_suppliers()
    return render_template('admin/manage_suppliers.html', suppliers=suppliers)

# ==========================================
# 4. الرقابة المالية والأرشفة (Financials & Logs)
# ==========================================
@admin_bp.route('/reports/sovereign')
@login_required
@admin_only
def financial_reports():
    # سيتم ربطها بمنطق الحسابات لاحقاً
    return render_template('admin/reports.html')
