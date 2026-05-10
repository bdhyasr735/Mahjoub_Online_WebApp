from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from admin_panel.suppliers_logic import SupplierLogic
from admin_panel import admin_bp 

# مسار تعميد مورد جديد
@admin_bp.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        # استخدام المحرك الموحد
        success, message = SupplierLogic.register_supplier(request.form)
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('admin.manage_suppliers'))
            
    next_id = SupplierLogic.get_next_id()
    return render_template('admin/add_supplier.html', next_id=next_id)

# مسار عرض الموردين (الرادار)
@admin_bp.route('/suppliers/manage')
@login_required
def manage_suppliers():
    search_query = request.args.get('search')
    status_filter = request.args.get('status')
    
    # جلب البيانات عبر المنطق
    suppliers = SupplierLogic.search_suppliers(query=search_query, status=status_filter)
    return render_template('admin/manage_suppliers.html', suppliers=suppliers)
