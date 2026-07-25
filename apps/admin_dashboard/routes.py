# coding: utf-8
# 📂 apps/admin_dashboard/routes.py

from flask import Blueprint, render_template, flash
from flask_login import login_required
from apps.extensions import db
from apps.models import Supplier, SupplierWallet, WalletTransaction
from sqlalchemy import func

admin_dashboard_bp = Blueprint(
    'admin_dashboard_bp', 
    __name__, 
    template_folder='templates'
)


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
        
        # ✅ عدد المنتجات (معالج آمن)
        try:
            from apps.models.product_db import Product
            product_count = db.session.query(func.count(Product.id)).scalar() or 0
        except:
            product_count = 0
        
        # ✅ عدد الطلبات والإيرادات (معالج آمن)
        try:
            from apps.models.orders_db import Order
            order_count = db.session.query(func.count(Order.id)).scalar() or 0
            
            # ✅ محاولة جلب الإيرادات
            if hasattr(Order, 'total_amount'):
                total_revenue = db.session.query(func.sum(Order.total_amount)).scalar() or 0.0
            elif hasattr(Order, 'total'):
                total_revenue = db.session.query(func.sum(Order.total)).scalar() or 0.0
            elif hasattr(Order, 'total_price'):
                total_revenue = db.session.query(func.sum(Order.total_price)).scalar() or 0.0
            else:
                total_revenue = 0.0
        except:
            order_count = 0
            total_revenue = 0.0
        
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
        
        return render_template('admin/dashboard.html', 
                               total_suppliers=0, 
                               total_products=0,
                               total_orders=0,
                               total_revenue=0.0,
                               total_balance_sar=0.0, 
                               total_balance_yer=0.0, 
                               total_balance_usd=0.0, 
                               recent_transactions=[])
