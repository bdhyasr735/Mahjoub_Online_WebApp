# coding: utf-8
from flask import render_template, request, jsonify
from flask_login import login_required
from apps.statement import statement_blueprint
from apps.models.supplier_db import Supplier
from apps.models.statement_db import SupplierStatement
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from sqlalchemy import or_

@statement_blueprint.route('/view', methods=['GET'])
@login_required
def view_statement():
    return render_template('admin/statement.html')

# API للبحث اللحظي (Autocomplete)
@statement_blueprint.route('/api/suppliers/search', methods=['GET'])
@login_required
def search_suppliers():
    term = request.args.get('q', '')
    suppliers = Supplier.query.filter(or_(
        Supplier.trade_name.ilike(f'%{term}%'),
        Supplier.sovereign_id.ilike(f'%{term}%'),
        Supplier.wallet_code.ilike(f'%{term}%')
    )).limit(10).all()
    
    return jsonify([{'id': s.id, 'text': f"{s.trade_name} - {s.sovereign_id}", 'wallet': s.wallet_code} for s in suppliers])

# API لجلب البيانات المالية المتكاملة
@statement_blueprint.route('/api/statement/data', methods=['GET'])
@login_required
def get_statement_data():
    supplier_id = request.args.get('id')
    supplier = Supplier.query.get(supplier_id)
    if not supplier: return jsonify({'error': 'Supplier not found'}), 404
    
    # جلب المحفظة
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier.sovereign_id).first()
    # جلب الكشف
    statements = SupplierStatement.query.filter_by(supplier_id=supplier.id).order_by(SupplierStatement.created_at.desc()).all()
    # حساب الأرباح من جدول المعاملات
    total_profit = sum(t.profit_margin for t in wallet.transactions) if wallet else 0
    
    return jsonify({
        'trade_name': supplier.trade_name,
        'wallet': {
            'yer': wallet.yer_total if wallet else 0,
            'sar': wallet.sar_total if wallet else 0,
            'usd': wallet.usd_total if wallet else 0
        },
        'total_profit': float(total_profit),
        'statements': [{
            'date': s.created_at.strftime('%Y-%m-%d'),
            'desc': s.description,
            'ref': s.reference_number,
            'debit': s.debit,
            'credit': s.credit,
            'balance': s.running_balance
        } for s in statements]
    })
