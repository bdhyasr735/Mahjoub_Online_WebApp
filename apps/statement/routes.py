# coding: utf-8
from flask import render_template, request, jsonify
from flask_login import login_required
from apps.extensions import db  # تم التأكد من استيراد db هنا
from apps.statement import statement_blueprint
from apps.models.supplier_db import Supplier
from apps.models.statement_db import SupplierStatement
from apps.models.wallet_db import SupplierWallet, WalletTransaction
from sqlalchemy import or_, func
from datetime import datetime

@statement_blueprint.route('/view', methods=['GET'])
@login_required
def view_statement():
    # العملات المتاحة للاختيار في الواجهة
    currencies = ['USD', 'YER', 'SAR'] 
    return render_template('admin/statement.html', currencies=currencies)

# 1. محرك البحث الذكي (Live Search) - مُنسق لـ Select2
@statement_blueprint.route('/api/suppliers/search', methods=['GET'])
@login_required
def api_search_suppliers():
    term = request.args.get('q', '')
    suppliers = Supplier.query.filter(or_(
        Supplier.trade_name.ilike(f'%{term}%'),
        Supplier.sovereign_id.ilike(f'%{term}%'),
        Supplier.wallet_code.ilike(f'%{term}%')
    )).limit(15).all()
    
    # تنسيق الـ JSON المطلوب لمكتبة Select2
    results = [{'id': s.id, 'text': f"{s.trade_name} | {s.sovereign_id} | {s.wallet_code}"} for s in suppliers]
    return jsonify({"results": results})

# 2. محرك جلب البيانات (التفصيلي والإجمالي) - بنظام AJAX
@statement_blueprint.route('/api/statement/report', methods=['GET'])
@login_required
def api_get_report():
    supplier_id = request.args.get('id')
    currency = request.args.get('currency', 'ALL')
    start_date = request.args.get('start')
    end_date = request.args.get('end')

    supplier = Supplier.query.get(supplier_id)
    if not supplier: 
        return jsonify({'error': 'المورد غير موجود'}), 404

    # 1. كشوفات الحساب (التفصيلي)
    stmt_query = SupplierStatement.query.filter_by(supplier_id=supplier.id)
    if currency != 'ALL':
        stmt_query = stmt_query.filter_by(currency=currency)
    if start_date and end_date:
        stmt_query = stmt_query.filter(SupplierStatement.created_at.between(start_date, end_date))
    
    statements = stmt_query.order_by(SupplierStatement.created_at.desc()).all()

    # 2. حساب الأرباح (من جدول WalletTransaction)
    wallet = SupplierWallet.query.filter_by(supplier_id=supplier.sovereign_id).first()
    total_profit = 0
    
    if wallet:
        # بناء استعلام الأرباح مع مراعاة الفلاتر
        profit_query = WalletTransaction.query.filter_by(wallet_id=wallet.id)
        if currency != 'ALL': 
            profit_query = profit_query.filter_by(currency=currency)
        if start_date and end_date: 
            profit_query = profit_query.filter(WalletTransaction.created_at.between(start_date, end_date))
        
        total_profit = profit_query.with_entities(func.sum(WalletTransaction.profit_margin)).scalar() or 0

    return jsonify({
        'summary': {
            'total_debit': sum(s.debit for s in statements),
            'total_credit': sum(s.credit for s in statements),
            'net_balance': sum(s.credit for s in statements) - sum(s.debit for s in statements),
            'total_profit': float(total_profit)
        },
        'details': [{
            'date': s.created_at.strftime('%Y-%m-%d %H:%M'),
            'desc': s.description or '---',
            'ref': s.reference_number or '---',
            'debit': s.debit,
            'credit': s.credit,
            'balance': s.running_balance
        } for s in statements]
    })
