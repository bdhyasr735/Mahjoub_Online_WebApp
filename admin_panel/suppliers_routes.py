# admin_panel/suppliers_routes.py
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from admin_panel.suppliers_logic import SupplierLogic

# ملاحظة: سنستخدم الـ blueprint الذي تم تعريفه في الـ __init__.py الخاص بالـ admin_panel
from admin_panel import admin_bp 

@admin_bp.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        # استدعاء المحرك الذي وحدنا مسمى دالته إلى register_supplier
        success, message = SupplierLogic.register_supplier(request.form)
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('admin.manage_suppliers'))
            
    next_id = SupplierLogic.get_next_id()
    return render_template('admin/add_supplier.html', next_id=next_id)

@admin_bp.route('/suppliers/manage')
@login_required
def manage_suppliers():
    search_query = request.args.get('search')
    status_filter = request.args.get('status')
    
    # استدعاء محرك البحث من المنطق
    suppliers = SupplierLogic.search_suppliers(query=search_query, status=status_filter)
    return render_template('admin/manage_suppliers.html', suppliers=suppliers)
