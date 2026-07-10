# coding: utf-8
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for
from flask_login import login_required, current_user

# استيراد الموديلات من المركز مباشرة
from apps.models import db, Supplier, Order, SupplierWallet

# تعريف الـ Blueprint
suppliers_dashboard_bp = Blueprint('suppliers_dashboard', __name__, template_folder='templates')

def check_supplier_access():
    """تحقق ذكي وآمن لمنع تداخل الجلسات وعدم طرد الموظفين"""
    user_type = session.get('user_type')
    
    # 1. إذا لم يكن مورد أو موظف مورد
    if user_type not in ['supplier', 'staff']:
        return False
        
    # 2. منع قاطع لدخول أي حساب إداري (AdminUser) إلى هنا لتجنب خطأ 500
    if current_user.__class__.__name__ == 'AdminUser':
        return False
        
    return True

@suppliers_dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    لوحة تحكم المورد والموظف الأساسية (Dashboard) - نسخة مصححة لخطأ 500.
    """
    if not check_supplier_access():
        flash("يرجى تسجيل الدخول بحساب المورد للوصول إلى لوحة التحكم.", "warning")
        return redirect('/supplier/login')
        
    user_type = session.get('user_type')
    
    # جلب المعرف المالي للمورد بناءً على كونه مالك الحساب أو موظف تابع بأمان
    if user_type == 'staff':
        supplier_id = getattr(current_user, 'supplier_id', None)
    else:
        supplier_id = getattr(current_user, 'id', None)
        
    if not supplier_id:
        return redirect('/supplier/login')
    
    supplier = db.session.get(Supplier, supplier_id)
    if not supplier:
        flash("لم يتم العثور على بيانات المورد الخاصة بك.", "danger")
        return redirect('/supplier/login')
        
    # ✨ الإصلاح الجذري: تم إضافة .unique() لإنهاء مشكلة الاستعلام المتداخل في الـ Logs وحل خطأ 500
    wallet = db.session.execute(
        db.select(SupplierWallet).filter_by(supplier_id=supplier.id)
    ).unique().scalar_one_or_none()
    
    supplier.wallet = wallet
    
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
    if not check_supplier_access():
        return redirect('/supplier/login')
        
    user_type = session.get('user_type')
    supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
    supplier = db.session.get(Supplier, supplier_id)
    
    if not supplier:
        abort(404)
    
    if request.method == 'POST':
        profile = supplier.supplier_profile
        if profile:
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

@suppliers_dashboard_bp.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if not check_supplier_access():
        return redirect('/supplier/login')
        
    user_type = session.get('user_type')
    supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
    supplier = db.session.get(Supplier, supplier_id)
    
    if not supplier:
        abort(404)
        
    # ✨ تطبيق إصلاح .unique() هنا أيضاً لضمان استقرار صفحة السحب ومنع تعطلها مستقبلاً
    wallet = db.session.execute(
        db.select(SupplierWallet).filter_by(supplier_id=supplier.id)
    ).unique().scalar_one_or_none()
    
    supplier.wallet = wallet
    
    return render_template('suppliers/withdraw.html', supplier=supplier)
