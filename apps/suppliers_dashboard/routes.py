# coding: utf-8
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for
from flask_login import login_required, current_user

# استيراد الموديلات من المركز مباشرة مع تصحيح المسميات
from apps.models import db, Supplier, Order, SupplierWallet

# تعريف الـ Blueprint
suppliers_dashboard_bp = Blueprint('suppliers_dashboard', __name__, template_folder='templates')

@suppliers_dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """
    لوحة تحكم المورد والموظف: تعرض الرصيد والإحصائيات بآمان وموثوقية عالية.
    """
    # 1. التحقق من صلاحية الوصول من الجلسة
    user_type = session.get('user_type')
    if user_type not in ['supplier', 'staff']:
        abort(403)
        
    # 2. جلب معرف المورد بناءً على نوع المستخدم (موظف أم مالك المورد)
    supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
    
    # 3. استخدام db.session.get الآمن لمنع تعليق الطلب (Internal Server Error 500)
    supplier = db.session.get(Supplier, supplier_id)
    
    if not supplier:
        abort(404)
        
    # 4. جلب محفظة المورد بشكل منفصل وآمن لإسنادها لكائن العرض
    wallet = db.session.execute(
        db.select(SupplierWallet).filter_by(supplier_id=supplier.id)
    ).scalar_one_or_none()
    
    # إسناد المحفظة يدوياً لضمان قراءتها في قالب الجينجا (HTML)
    supplier.wallet = wallet
    
    # 5. حساب الطلبات المعلقة (pending) الخاصة بالمورد
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
    user_type = session.get('user_type')
    if user_type not in ['supplier', 'staff']:
        abort(403)
        
    supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
    supplier = db.session.get(Supplier, supplier_id)
    
    if not supplier:
        abort(404)
    
    # معالجة تحديث البيانات عند تقديم النموذج
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
    """
    صفحة السحب المالي للمورد والموظف المصرح له.
    """
    user_type = session.get('user_type')
    if user_type not in ['supplier', 'staff']:
        abort(403)
        
    supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
    supplier = db.session.get(Supplier, supplier_id)
    
    if not supplier:
        abort(404)
        
    # جلب المحفظة بشكل آمن ومنفصل ومقاوم للأخطاء الصامتة
    wallet = db.session.execute(
        db.select(SupplierWallet).filter_by(supplier_id=supplier.id)
    ).scalar_one_or_none()
    
    supplier.wallet = wallet
    
    return render_template('suppliers/withdraw.html', supplier=supplier)
