# 📂 apps/wallet/routes.py
from flask import Blueprint, render_template, request, jsonify
from apps.extensions import db
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from apps.models.supplier_db import Supplier
from datetime import datetime

wallet_app = Blueprint('wallet_app', __name__)

# متغير لتحديد فترة الحداد
IS_MOURNING_PERIOD = True 

@wallet_app.route('/dashboard')
def dashboard():
    # في حالة الحداد، نعيد الواجهة العامة دون بيانات أو برسالة حداد
    return render_template('admin/wallet_app.html', 
                           total_system_sar=0, 
                           total_system_yer=0, 
                           total_system_usd=0,
                           is_mourning=IS_MOURNING_PERIOD)

@wallet_app.route('/view/<int:supplier_id>')
def view_wallet(supplier_id):
    if IS_MOURNING_PERIOD:
        return render_template('admin/view_wallet.html', is_mourning_period=True)

    page = request.args.get('page', 1, type=int)
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier_id).first_or_404()
    transactions = WalletTransaction.query.filter_by(wallet_id=wallet.id)\
        .order_by(WalletTransaction.created_at.desc())\
        .paginate(page=page, per_page=10)
    
    return render_template('admin/view_wallet.html', 
                           wallet=wallet, 
                           transactions=transactions,
                           is_mourning_period=False)

@wallet_app.route('/api/search')
def search_suppliers():
    if IS_MOURNING_PERIOD:
        return jsonify({'results': []})
        
    query = request.args.get('q', '')
    suppliers = Supplier.query.filter(
        (Supplier.trade_name.contains(query)) | 
        (Supplier.owner_phone.contains(query))
    ).limit(10).all()
    
    return jsonify({
        'results': [{'id': s.id, 'name': s.trade_name, 'phone': s.owner_phone} for s in suppliers]
    })
