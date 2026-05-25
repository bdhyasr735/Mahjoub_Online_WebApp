# coding: utf-8
from flask import render_template, request, jsonify
from flask_login import login_required
from apps.extensions import db
from apps.statement import statement_blueprint
from apps.models.supplier_db import Supplier
from apps.models.statement_db import SupplierStatement
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from sqlalchemy import or_, func

@statement_blueprint.route('/view', methods=['GET'])
@login_required
def view_statement():
    currencies = ['USD', 'YER', 'SAR'] 
    return render_template('admin/statement.html', currencies=currencies)

# 1. محرك البحث الذكي (Live Search)
@statement_blueprint.route('/api/suppliers/search', methods=['GET'])
@login_required
def api_search_suppliers():
    term = request.args.get('q', '')
    suppliers = Supplier.query.filter(or_(
        Supplier.trade_name.ilike(f'%{term}%'),
        Supplier.sovereign_id.ilike(f'%{term}%'),
        Supplier.store_name.ilike(f'%{term}%'),
        Supplier.owner_name.ilike(f'%{term}%')
    )).limit(15).all()
    
    # تنسيق للـ Select2
    results = [{'id': s.id, 'text': f"{s.trade_name} - المتجر: {s.store_name} - {s.sovereign_id}"} for s in suppliers]
    return jsonify({"results": results})

# 2. محرك جلب البيانات (التفصيلي والإجمالي)
@statement_blueprint.route('/api/statement/report', methods=['GET'])
@login_required
def api_get_report():
    supplier_id = request.args.get('id')
    currency = request.args.get('currency', 'ALL')
    start = request.args.get('start')
    end = request.args.get('end')

    supplier = Supplier.query.get(supplier_id)
    if not supplier: return jsonify({'error': 'المورد غير موجود'}), 404

    # كشوفات الحساب
    stmt_query = SupplierStatement.query.filter_by(supplier_id=supplier.id)
    if currency != 'ALL': stmt_query = stmt_query.filter_by(currency=currency)
    if start and end: stmt_query = stmt_query.filter(SupplierStatement.created_at.between(start, end))
    statements = stmt_query.order_by(SupplierStatement.created_at.desc()).all()

    # حساب الأرباح (WalletTransaction)
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier.sovereign_id).first()
    profit = 0
    if wallet:
        pq = WalletTransaction.query.filter_by(wallet_id=wallet.id)
        if currency != 'ALL': pq = pq.filter_by(currency=currency)
        if start and end: pq = pq.filter(WalletTransaction.created_at.between(start, end))
        profit = pq.with_entities(func.sum(WalletTransaction.profit_margin)).scalar() or 0

    return jsonify({
        'summary': {
            'total_debit': sum(s.debit for s in statements),
            'total_credit': sum(s.credit for s in statements),
            'net_balance': sum(s.credit for s in statements) - sum(s.debit for s in statements),
            'total_profit': float(profit)
        },
        'details': [{'date': s.created_at.strftime('%Y-%m-%d %H:%M'), 'desc': s.description, 'ref': s.reference_number, 'debit': s.debit, 'credit': s.credit, 'balance': s.running_balance} for s in statements]
    })
