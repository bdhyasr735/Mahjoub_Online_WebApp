# coding: utf-8
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for
from flask_login import login_required, current_user

# استيراد الموديلات والـ DB من الحزمة المركزية
from apps.models import db, Supplier, Order, SupplierWallet

# تعريف الـ Blueprint
suppliers_dashboard_bp = Blueprint('suppliers_dashboard', __name__, template_folder='templates')

def get_supplier_context():
    """دالة مساعدة لجلب المورد والمحفظة بأمان لتقليل التكرار"""
    user_type = session.get('user_type')
    if user_type not in ['supplier', 'staff']:
        return None
        
    supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
    supplier = db.session.get(Supplier, supplier_id)
    
    if supplier:
        # استخدام unique() لحل مشاكل تضارب الاستعلامات في SqlAlchemy
        wallet = db.session.execute(
            db.select(SupplierWallet).filter_by(supplier_id=supplier.id)
        ).unique().scalar_one_or_none()
        supplier.wallet = wallet
        
    return supplier

@suppliers_dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """لوحة التحكم الرئيسية"""
    supplier = get_supplier_context()
    if not supplier:
        return redirect('/supplier/login')
        
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
    """صفحة إعدادات المورد"""
    supplier = get_supplier_context()
    if not supplier:
        return redirect('/supplier/login')
    
    if request.method == 'POST':
        profile = getattr(supplier, 'supplier_profile', None)
        if profile:
            profile.owner_name = request.form.get('owner_name')
            profile.email = request.form.get('email')
            profile.address = request.form.get('address')
        
        try:
            db.session.commit()
            flash('تم تحديث البيانات بنجاح', 'success')
        except Exception:
            db.session.rollback()
            flash('حدث خطأ أثناء حفظ البيانات', 'danger')
            
        return redirect(url_for('suppliers_dashboard.settings'))
        
    return render_template('suppliers/settings.html', supplier=supplier)

@suppliers_dashboard_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    """صفحة السحب من المحفظة"""
    supplier = get_supplier_context()
    if not supplier:
        return redirect('/supplier/login')
    
    # هنا ستتم إضافة منطق معالجة طلب السحب لاحقاً
    return render_template('suppliers/withdraw.html', supplier=supplier)
