# coding: utf-8
from flask import render_template, request
from flask_login import login_required
from apps.statement import statement_blueprint
from apps.models.supplier_db import Supplier
from apps.models.statement_db import SupplierStatement
from sqlalchemy import or_

@statement_blueprint.route('/view', methods=['GET'])
@login_required
def view_statement():
    q = request.args.get('q', '')
    currency = request.args.get('currency', 'ALL')
    report_type = request.args.get('report_type', 'detailed')
    
    # جلب جميع الموردين للقائمة المنسدلة
    all_suppliers = Supplier.query.all()
    
    selected_supplier = None
    statements = []

    if q:
        # البحث بالاسم أو المعرف
        selected_supplier = Supplier.query.filter(or_(
            Supplier.trade_name.ilike(f'%{q}%'),
            Supplier.sovereign_id == q
        )).first()
        
        if selected_supplier:
            query = SupplierStatement.query.filter_by(supplier_id=selected_supplier.id)
            
            # تطبيق فلتر العملة
            if currency != 'ALL':
                query = query.filter_by(currency=currency)
            
            statements = query.order_by(SupplierStatement.created_at.desc()).all()

    return render_template(
        'admin/statement.html',
        all_suppliers=all_suppliers,
        selected_supplier=selected_supplier,
        statements=statements,
        report_type=report_type,
        currency_filter=currency
    )
