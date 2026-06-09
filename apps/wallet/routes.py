# 📂 apps/wallet/routes.py
from flask import render_template, request, jsonify
from flask_login import login_required
from sqlalchemy import func
from apps import db 
from apps.models.wallet_db import SupplierWallet as Wallet, WalletTransaction as Transaction
from apps.models.supplier_db import Supplier
from apps.wallet import wallet_app

# مسار الداشبورد الرئيسي
@wallet_app.route('/wallet_dashboard')
@login_required
def wallet_dashboard():
    stats = {
        "usd": db.session.query(func.sum(Wallet.balance_usd)).scalar() or 0,
        "sar": db.session.query(func.sum(Wallet.balance_sar)).scalar() or 0,
        "yer": db.session.query(func.sum(Wallet.balance_yer)).scalar() or 0,
        "count": Wallet.query.count()
    }
    return render_template('admin/wallet_app.html', stats=stats)

# محرك جلب الموردين (يغذي الجدول)
@wallet_app.get('/get_suppliers_list')
@login_required
def get_suppliers_list():
    page = request.args.get('page', 1, type=int)
    suppliers = Supplier.query.paginate(page=page, per_page=10, error_out=False)
    # ملاحظة: suppliers_list.html يجب أن يكون ملفاً جزئياً (Partial) بدون {% extends %}
    return render_template('admin/suppliers_list.html', suppliers=suppliers)

# محرك عرض المحفظة (يغذي منطقة العرض)
@wallet_app.get('/view/<int:supplier_id>')
@login_required
def view_wallet(supplier_id):
    wallet = Wallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    transactions = Transaction.query.filter_by(wallet_id=wallet.id)\
        .order_by(Transaction.created_at.desc())\
        .paginate(page=1, per_page=10, error_out=False)
    return render_template('admin/view_wallet.html', wallet=wallet, transactions=transactions)
