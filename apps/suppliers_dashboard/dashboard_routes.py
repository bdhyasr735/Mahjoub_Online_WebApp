# coding: utf-8
# 📂 apps/suppliers_dashboard/routes/dashboard_routes.py

from flask import Blueprint, render_template, session, redirect
from flask_login import login_required, current_user

from apps.models import db, Supplier, Order, SupplierWallet

suppliers_dashboard_bp = Blueprint(
    'suppliers_dashboard',
    __name__,
    template_folder='templates'
)


@suppliers_dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    try:
        # ✅ جلب المورد
        user_type = session.get('user_type')
        supplier_id = current_user.supplier_id if user_type == 'staff' else current_user.id
        supplier = db.session.get(Supplier, supplier_id)
        
        if not supplier:
            return "❌ المورد غير موجود", 404
        
        # ✅ جلب المحفظة
        wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
        supplier.wallet = wallet
        
        # ✅ عدد الطلبات
        pending_orders_count = Order.query.filter_by(
            supplier_id=supplier.id, status='pending'
        ).count()
        
        # ✅ عرض الصفحة
        return render_template(
            'suppliers/dashboard.html',
            supplier=supplier,
            pending_orders_count=pending_orders_count,
            total_sales=0
        )
        
    except Exception as e:
        return f"""
        <div style="direction: rtl; font-family: Tahoma; padding: 30px; text-align: center;">
            <h2 style="color: #d9534f;">❌ خطأ</h2>
            <p>{str(e)}</p>
            <a href="/supplier/dashboard" style="background: #2d0b36; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px;">محاولة مرة أخرى</a>
        </div>
        """, 500
