# 📂 apps/wallet/routes.py - المحرك المالي الاحترافي
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from sqlalchemy import func
from apps.extensions import db
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import SupplierWallet, WalletTransaction

# تعريف المحرك
wallet_app = Blueprint('wallet_app', __name__)

@wallet_app.route('/view/<int:supplier_id>')
@login_required
def view_wallet(supplier_id):
    # 1. جلب بيانات المورد والمحفظة
    supplier = Supplier.query.get_or_404(supplier_id)
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier.id).first()
    
    if not wallet:
        return "هذا المورد لا يمتلك محفظة حالياً.", 404

    # 2. الترقيم (Pagination): عرض 10 إلى 20 عملية حسب اختيارك
    page = request.args.get('page', 1, type=int)
    
    # جلب العمليات مع الترقيم
    pagination = WalletTransaction.query.filter_by(wallet_id=wallet.id)\
        .order_by(WalletTransaction.created_at.desc())\
        .paginate(page=page, per_page=15, error_out=False) # تم ضبطه على 15 عملية
    
    transactions = pagination.items
    
    # 3. إرسال البيانات
    return render_template('admin/wallet_app_detail.html', 
                           supplier=supplier, 
                           wallet=wallet, 
                           transactions=transactions,
                           pagination=pagination)

@wallet_app.route('/stats')
@login_required
def get_stats():
    # حساب إجمالي أرصدة النظام
    totals = db.session.query(
        func.sum(SupplierWallet.balance_sar),
        func.sum(SupplierWallet.balance_yer),
        func.sum(SupplierWallet.balance_usd)
    ).first()
    
    return jsonify({
        'sar': float(totals[0] or 0),
        'yer': float(totals[1] or 0),
        'usd': float(totals[2] or 0)
    })
