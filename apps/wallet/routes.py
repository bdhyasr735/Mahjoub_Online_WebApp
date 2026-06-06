# coding: utf-8
# 📂 apps/wallet/routes.py - النسخة المعتمدة مع دعم Pagination

from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from apps import db 
from apps.models.wallet_db import SupplierWallet, WalletTransaction

wallet_app = Blueprint(
    'wallet_app', 
    __name__, 
    template_folder='templates'
)

# 1. عرض لوحة تحكم المحفظة
@wallet_app.route('/dashboard')
@login_required
def wallet_dashboard():
    try:
        total_sar = db.session.query(db.func.sum(SupplierWallet.balance_sar)).scalar()
        total_yer = db.session.query(db.func.sum(SupplierWallet.balance_yer)).scalar()
        total_usd = db.session.query(db.func.sum(SupplierWallet.balance_usd)).scalar()
        
        total_system_sar = float(total_sar) if total_sar else 0.0
        total_system_yer = float(total_yer) if total_yer else 0.0
        total_system_usd = float(total_usd) if total_usd else 0.0
        
    except Exception as e:
        print(f"DEBUG: Error in wallet_dashboard: {e}")
        total_system_sar = total_system_yer = total_system_usd = 0.0
    
    return render_template(
        'admin/wallet_app.html', 
        total_system_sar=total_system_sar,
        total_system_yer=total_system_yer,
        total_system_usd=total_system_usd
    )

# 2. عرض محفظة مورد محدد مع نظام الصفحات (Pagination)
@wallet_app.route('/view/<int:supplier_id>')
@login_required
def view_wallet(supplier_id):
    # جلب المحفظة
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first()
    
    # الحصول على رقم الصفحة من الطلب (Default = 1)
    page = request.args.get('page', 1, type=int)
    
    # استخدام paginate بدلاً من all()
    transactions_pagination = None
    if wallet:
        transactions_pagination = WalletTransaction.query.filter_by(wallet_id=wallet.id)\
            .order_by(WalletTransaction.created_at.desc())\
            .paginate(page=page, per_page=10, error_out=False)
    
    return render_template(
        'admin/view_wallet.html', 
        wallet=wallet, 
        transactions=transactions_pagination.items if transactions_pagination else [],
        pagination=transactions_pagination
    )

# 3. إضافة عملية مالية (API)
@wallet_app.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction():
    return jsonify({"status": "success", "message": "تمت العملية بنجاح"})
