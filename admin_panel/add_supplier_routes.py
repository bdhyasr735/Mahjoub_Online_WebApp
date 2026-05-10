# admin_panel/add_supplier_routes.py
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from admin_panel.suppliers_logic import SupplierLogic
from admin_panel import admin_bp 

# --- مسار تعميد مورد جديد ---
@admin_bp.route('/suppliers/add', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        # إرسال البيانات للمنطق لتنفيذ التعميد والأرشفة
        success, message = SupplierLogic.register_supplier(request.form)
        
        # إظهار رسالة النتيجة في الواجهة الملكية
        flash(message, 'success' if success else 'danger')
        
        if success:
            # التوجيه للرادار بعد النجاح
            return redirect(url_for('admin.manage_suppliers'))
            
    # توليد المعرف السيادي القادم لعرضه في الصفحة (Read-only)
    next_id = SupplierLogic.get_next_id()
    return render_template('admin/add_supplier.html', next_id=next_id)


# --- مسار إدارة الموردين (الرادار السيادي) ---
@admin_bp.route('/suppliers/manage')
@login_required
def manage_suppliers():
    # استقبال فلاتر البحث من شريط البحث في الواجهة
    search_query = request.args.get('search')
    status_filter = request.args.get('status')
    
    # جلب قائمة الموردين المعتمدين عبر المنطق
    suppliers = SupplierLogic.search_suppliers(query=search_query, status=status_filter)
    
    return render_template('admin/manage_suppliers.html', suppliers=suppliers)
