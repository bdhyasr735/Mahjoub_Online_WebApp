# coding: utf-8
# 📂 apps/suppliers_dashboard/routes/dashboard_routes.py

from flask import Blueprint, render_template, abort, session, redirect, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
import traceback

from apps.models import db, Supplier, Order, SupplierWallet, OrderFinancial

suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    template_folder='templates'
)


def get_supplier_context():
    """جلب المورد والمحفظة من قاعدة البيانات"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            return None
            
        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
        supplier = db.session.get(Supplier, supplier_id)
        
        if supplier:
            wallet = db.session.execute(
                db.select(SupplierWallet).filter_by(supplier_id=supplier.id)
            ).unique().scalar_one_or_none()
            supplier.wallet = wallet
            
        return supplier
    except Exception as e:
        print(f"❌ خطأ في get_supplier_context: {e}")
        return None


@suppliers_dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """لوحة تحكم المورد الرئيسية"""
    try:
        supplier = get_supplier_context()
        if not supplier:
            return redirect('/supplier/login')
        
        # ✅ عدد الطلبات قيد التنفيذ
        try:
            pending_orders_count = Order.query.filter_by(
                supplier_id=supplier.id, status='pending'
            ).count()
        except Exception as e:
            print(f"⚠️ خطأ في جلب الطلبات: {e}")
            pending_orders_count = 0
        
        # ✅ حساب إجمالي المبيعات
        try:
            total_sales = db.session.query(
                func.sum(OrderFinancial.total_paid_raw)
            ).join(Order, Order.id == OrderFinancial.order_id).filter(
                Order.supplier_id == supplier.id,
                Order.status == 'completed'
            ).scalar() or 0
        except Exception as e:
            print(f"⚠️ خطأ في حساب المبيعات: {e}")
            total_sales = 0
        
        # ✅ عرض الصفحة
        return render_template(
            'suppliers/dashboard.html',
            supplier=supplier,
            pending_orders_count=pending_orders_count,
            total_sales=float(total_sales)
        )
        
    except Exception as e:
        # ✅ عرض الخطأ في الصفحة بدلاً من 500
        error_details = traceback.format_exc()
        print(f"❌ خطأ في dashboard: {error_details}")
        
        return f"""
        <div style="direction: rtl; font-family: Tahoma; padding: 30px; text-align: center;">
            <h2 style="color: #d9534f;">❌ حدث خطأ في لوحة التحكم</h2>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: right; margin: 20px auto; max-width: 800px; overflow: auto;">
                <p><strong>الخطأ:</strong></p>
                <pre style="background: #fff; padding: 15px; border-radius: 5px; border: 1px solid #ddd; font-size: 12px; line-height: 1.6;">{error_details}</pre>
            </div>
            <a href="/supplier/dashboard" style="background: #2d0b36; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px;">محاولة مرة أخرى</a>
        </div>
        """, 500
