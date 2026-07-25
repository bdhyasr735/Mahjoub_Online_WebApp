# coding: utf-8
# 📂 apps/admin_dashboard/routes.py

from flask import Blueprint, render_template, flash
from flask_login import login_required
from apps.extensions import db
from apps.models import Supplier, SupplierWallet, WalletTransaction, Product, Order
from sqlalchemy import func

# 1. تعريف الـ Blueprint
admin_dashboard_bp = Blueprint(
    'admin_dashboard_bp', 
    __name__, 
    template_folder='templates'
)

# 2. مسار لوحة التحكم
@admin_dashboard_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    """عرض لوحة تحكم النظام الرئيسية"""
    
    try:
        # ✅ إجمالي الأرصدة
        totals = db.session.query(
            func.sum(SupplierWallet.balance_sar).label('total_sar'),
            func.sum(SupplierWallet.balance_yer).label('total_yer'),
            func.sum(SupplierWallet.balance_usd).label('total_usd')
        ).first()
        
        # ✅ عدد الموردين
        supplier_count = db.session.query(func.count(Supplier.id)).scalar() or 0
        
        # ✅ عدد المنتجات
        product_count = db.session.query(func.count(Product.id)).scalar() or 0
        
        # ✅ عدد الطلبات
        order_count = db.session.query(func.count(Order.id)).scalar() or 0
        
        # ✅ إجمالي الإيرادات (مجموع total_amount من الطلبات)
        total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0.0
        
        # ✅ آخر 10 معاملات مالية
        recent_transactions = WalletTransaction.query.order_by(
            WalletTransaction.created_at.desc()
        ).limit(10).all()

        context = {
            "total_suppliers": supplier_count,
            "total_products": product_count,
            "total_orders": order_count,
            "total_revenue": float(total_revenue),
            "total_balance_sar": float(totals.total_sar or 0),
            "total_balance_yer": float(totals.total_yer or 0),
            "total_balance_usd": float(totals.total_usd or 0),
            "recent_transactions": recent_transactions
        }
        
        return render_template('admin/dashboard.html', **context)

    except Exception as e:
        print(f"❌ [Dashboard Error]: {str(e)}")
        flash("حدث خطأ أثناء تحميل بيانات لوحة التحكم، يرجى المحاولة لاحقاً.", "danger")
        
        # ✅ القيم الافتراضية في حالة الخطأ
        return render_template('admin/dashboard.html', 
                               total_suppliers=0, 
                               total_products=0,
                               total_orders=0,
                               total_revenue=0.0,
                               total_balance_sar=0.0, 
                               total_balance_yer=0.0, 
                               total_balance_usd=0.0, 
                               recent_transactions=[])
