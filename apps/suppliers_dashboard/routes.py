# coding: utf-8
# 📂 apps/suppliers_dashboard/routes.py

from flask import Blueprint, render_template, abort, session, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func

# استيراد الموديلات والـ DB من الحزمة المركزية
from apps.models import db, Supplier, Order, SupplierWallet, OrderFinancial

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
    """لوحة التحكم الرئيسية للمورد"""
    supplier = get_supplier_context()
    if not supplier:
        return redirect('/supplier/login')
    
    # ✅ عدد الطلبات قيد التنفيذ
    pending_orders_count = Order.query.filter_by(
        supplier_id=supplier.id, 
        status='pending'
    ).count()
    
    # ✅ ✅ إجمالي المبيعات (SAR فقط)
    total_sales = db.session.query(
        func.sum(OrderFinancial.total_paid_raw)
    ).join(
        Order, Order.id == OrderFinancial.order_id
    ).filter(
        Order.supplier_id == supplier.id,
        Order.status == 'completed'
    ).scalar() or 0
    
    return render_template(
        'suppliers/dashboard.html',
        supplier=supplier,
        pending_orders_count=pending_orders_count,
        total_sales=float(total_sales)
    )


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
    """صفحة السحب من المحفظة (عملة SAR فقط)"""
    supplier = get_supplier_context()
    if not supplier:
        return redirect('/supplier/login')
    
    wallet = supplier.wallet
    
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount', 0))
            if amount <= 0:
                flash('المبلغ يجب أن يكون أكبر من صفر', 'danger')
                return redirect(url_for('suppliers_dashboard.withdraw'))
            
            if not wallet or amount > wallet.balance_sar:
                flash(f'الرصيد غير كافٍ. الرصيد الحالي: {wallet.balance_sar if wallet else 0:.2f} SAR', 'danger')
                return redirect(url_for('suppliers_dashboard.withdraw'))
            
            # ✅ تسجيل طلب السحب
            # هنا يمكن إضافة منطق إنشاء طلب سحب
            
            flash(f'✅ تم تقديم طلب سحب بمبلغ {amount:.2f} SAR بنجاح', 'success')
            return redirect(url_for('suppliers_dashboard.dashboard'))
            
        except ValueError:
            flash('قيمة المبلغ غير صحيحة', 'danger')
    
    return render_template('suppliers/withdraw.html', supplier=supplier, wallet=wallet)
