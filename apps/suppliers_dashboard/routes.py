# coding: utf-8
from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for
from flask_login import login_required, current_user
from apps.models.supplier_db import Supplier, db
from apps.models.orders_db import Order

# تعريف الـ Blueprint
suppliers_dashboard_bp = Blueprint('suppliers_dashboard', __name__, template_folder='templates')

@suppliers_dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # التحقق من صلاحية المورد
    if session.get('user_type') != 'supplier':
        abort(403)
        
    supplier = Supplier.query.get(current_user.id)
    
    # حساب الطلبات المعلقة عبر الاستعلام المباشر
    pending_orders_count = Order.query.filter_by(
        supplier_id=supplier.id, 
        status='pending'
    ).count()
    
    return render_template('suppliers/dashboard.html', 
                           supplier=supplier, 
                           pending_orders_count=pending_orders_count)

@suppliers_dashboard_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if session.get('user_type') != 'supplier':
        abort(403)
        
    supplier = Supplier.query.get(current_user.id)
    
    # معالجة تحديث البيانات
    if request.method == 'POST':
        profile = supplier.supplier_profile
        profile.owner_name = request.form.get('owner_name')
        profile.email = request.form.get('email')
        profile.address = request.form.get('address')
        
        try:
            db.session.commit()
            flash('تم تحديث البيانات بنجاح', 'success')
        except Exception:
            db.session.rollback()
            flash('حدث خطأ أثناء حفظ البيانات، حاول مجدداً', 'danger')
            
        return redirect(url_for('suppliers_dashboard.settings'))
        
    return render_template('suppliers/settings.html', supplier=supplier)
