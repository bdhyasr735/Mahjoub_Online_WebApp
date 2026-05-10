from flask import render_template, request, jsonify
from . import admin_bp
from .suppliers_logic import SupplierManager # المحرك الخاص بهذه النافذة
from core.factory import SovereignFactory     # المصنع المركزي الشامل

# --- 1. مسارات عرض الواجهات (Render Routes) ---

@admin_bp.route('/dashboard')
def dashboard():
    # استدعاء من مجلد templates/admin/
    return render_template('admin/dashboard.html')

@admin_bp.route('/add-supplier', methods=['GET'])
def add_supplier_view():
    # حساب المعرف القادم يوضع في المنطق الخاص بالنافذة
    next_id = SupplierManager.get_next_id()
    return render_template('admin/add_supplier.html', next_id=next_id)

# --- 2. مسارات العمليات (Action Routes) ---

@admin_bp.route('/add-supplier', methods=['POST'])
def add_supplier_action():
    """
    هنا السحر: نرسل البيانات للمصنع المركزي مباشرة.
    المصنع سيتولى: الحفظ في DB، تشفير الباسورد، والأرشفة في GitHub.
    """
    return SovereignFactory.create_and_archive(
        model_name='Supplier', 
        data=request.form,
        files=request.files # في حال وجود صورة الهوية
    )

@admin_bp.route('/manage-suppliers')
def manage_suppliers():
    # جلب البيانات يتم عبر سطر واحد من المنطق
    suppliers = SupplierManager.get_all_active()
    return render_template('admin/manage_suppliers.html', suppliers=suppliers)
