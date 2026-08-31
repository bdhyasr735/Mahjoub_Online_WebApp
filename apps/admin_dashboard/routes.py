# -*- coding: utf-8 -*-
# 📂 apps/admin_dashboard/routes.py

from flask import Blueprint, render_template, flash
from flask_login import login_required
from apps.extensions import db

admin_dashboard_bp = Blueprint(
    'admin_dashboard', 
    __name__, 
    template_folder='templates',
    url_prefix='/admin'  # تعيين بادئة الرابط لتصبح /admin
)

@admin_dashboard_bp.route('/dashboard', methods=['GET'])  # ليصبح الرابط النهائي /admin/dashboard
@login_required
def dashboard():
    """عرض لوحة تحكم النظام الرئيسية بشكل آمن تام"""
    total_sar = 0.0
    total_yer = 0.0
    total_usd = 0.0
    supplier_count = 0
    product_count = 0
    order_count = 0
    total_revenue = 0.0
    recent_transactions = []

    try:
        try:
            from apps.models.wallet_db import SupplierWallet
            totals = db.session.query(
                db.func.sum(SupplierWallet.balance_sar).label('total_sar'),
                db.func.sum(SupplierWallet.balance_yer).label('total_yer'),
                db.func.sum(SupplierWallet.balance_usd).label('total_usd')
            ).first()
            if totals:
                total_sar = float(totals.total_sar or 0)
                total_yer = float(totals.total_yer or 0)
                total_usd = float(totals.total_usd or 0)
        except Exception as e:
            print(f"⚠️ [Wallet Error Skipped]: {e}")

        try:
            from apps.models.supplier_db import Supplier
            supplier_count = db.session.query(db.func.count(Supplier.id)).scalar() or 0
        except Exception as e:
            print(f"⚠️ [Supplier Error Skipped]: {e}")
        
        try:
            from apps.models.product_db import Product
            product_count = db.session.query(db.func.count(Product.id)).scalar() or 0
        except Exception as e:
            print(f"⚠️ [Product Error Skipped]: {e}")
        
        try:
            from apps.models.orders_db import Order
            order_count = db.session.query(db.func.count(Order.id)).scalar() or 0
            if hasattr(Order, 'total_amount'):
                total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0.0
            elif hasattr(Order, 'total'):
                total_revenue = db.session.query(db.func.sum(Order.total)).scalar() or 0.0
        except Exception as e:
            print(f"⚠️ [Order Error Skipped]: {e}")
        
        try:
            from apps.models.wallet_db import WalletTransaction
            recent_transactions = WalletTransaction.query.order_by(
                WalletTransaction.created_at.desc()
            ).limit(10).all()
        except Exception as e:
            print(f"⚠️ [Transactions Error Skipped]: {e}")

    except Exception as general_err:
        print(f"❌ [Dashboard General Error]: {str(general_err)}")

    context = {
        "total_suppliers": supplier_count,
        "total_products": product_count,
        "total_orders": order_count,
        "total_revenue": float(total_revenue),
        "total_balance_sar": total_sar,
        "total_balance_yer": total_yer,
        "total_balance_usd": total_usd,
        "recent_transactions": recent_transactions
    }
    
    return render_template('admin/dashboard.html', **context)
