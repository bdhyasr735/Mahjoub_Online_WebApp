# coding: utf-8
# 📂 apps/suppliers_dashboard/routes/dashboard_routes.py

from flask import Blueprint, render_template, session, redirect, jsonify
from flask_login import login_required, current_user
import traceback

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
        # ✅ جلب نوع المستخدم
        user_type = session.get('user_type')
        
        # ✅ التحقق من وجود user_type
        if user_type not in ['supplier', 'staff']:
            return "❌ نوع المستخدم غير معروف", 400
        
        # ✅ جلب supplier_id بأمان
        if user_type == 'staff':
            supplier_id = getattr(current_user, 'supplier_id', None)
        else:
            supplier_id = current_user.id
        
        # ✅ التحقق من وجود supplier_id
        if not supplier_id:
            return "❌ لا يوجد مورد مرتبط بهذا الحساب", 404
        
        # ✅ جلب المورد
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
        # ✅ عرض تفاصيل الخطأ كاملة
        error_details = traceback.format_exc()
        print(f"❌ خطأ في dashboard: {error_details}")
        
        return f"""
        <div style="direction: rtl; font-family: Tahoma; padding: 30px; text-align: center;">
            <h2 style="color: #d9534f;">❌ خطأ في لوحة التحكم</h2>
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: right; margin: 20px auto; max-width: 800px; overflow: auto; border: 1px solid #ddd;">
                <p><strong>تفاصيل الخطأ:</strong></p>
                <pre style="background: #fff; padding: 15px; border-radius: 5px; border: 1px solid #ddd; font-size: 12px; line-height: 1.6; white-space: pre-wrap; word-wrap: break-word;">{error_details}</pre>
            </div>
            <a href="/supplier/dashboard" style="background: #2d0b36; color: #fff; padding: 10px 20px; text-decoration: none; border-radius: 5px;">محاولة مرة أخرى</a>
        </div>
        """, 500
