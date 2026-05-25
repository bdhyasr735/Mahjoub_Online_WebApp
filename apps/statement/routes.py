# coding: utf-8
from flask import render_template, request, flash
from flask_login import login_required
from apps.statement import statement_blueprint
from sqlalchemy import or_

@statement_blueprint.route('/view', methods=['GET'])
@login_required
def view_statement():
    # الاستيراد داخل الدالة فقط - الحل السحري لمنع Circular Import
    from apps.models.supplier_db import Supplier
    from apps.models.statement_db import SupplierStatement

    q = request.args.get('q', '')
    currency = request.args.get('currency', 'ALL')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    selected_supplier = None
    statements = []

    if q:
        try:
            # البحث عن المورد
            selected_supplier = Supplier.query.filter(or_(
                Supplier.trade_name.ilike(f'%{q}%'),
                Supplier.owner_name.ilike(f'%{q}%'),
                Supplier.sovereign_id == q
            )).first()
            
            if selected_supplier:
                query = SupplierStatement.query.filter_by(supplier_id=selected_supplier.id)
                
                if currency != 'ALL':
                    query = query.filter_by(currency=currency)
                if start_date:
                    query = query.filter(SupplierStatement.created_at >= start_date)
                if end_date:
                    query = query.filter(SupplierStatement.created_at <= end_date)
                
                statements = query.order_by(SupplierStatement.created_at.desc()).all()
            else:
                flash("لم يتم العثور على مورد بهذه البيانات.", "warning")
        except Exception as e:
            flash("حدث خطأ تقني.", "danger")

    return render_template('admin/statement.html', selected_supplier=selected_supplier, statements=statements)
