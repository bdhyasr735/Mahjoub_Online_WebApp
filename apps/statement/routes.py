# coding: utf-8
from flask import render_template, request
from flask_login import login_required
from apps.statement import statement_blueprint
from apps.models.supplier_db import Supplier
# تأكد من استيراد الموديل الذي يحتوي على جدول حركات الكشوفات (الذي تربط به العلاقة)
from apps.models.statement_db import SupplierStatement 

@statement_blueprint.route('/view', methods=['GET'])
@login_required
def view_statement():
    # 1. جلب قائمة كل الموردين
    all_suppliers = Supplier.query.all()
    
    # 2. جلب معرف المورد
    supplier_id = request.args.get('supplier_id')
    selected_supplier = None
    statements = []
    # الرصيد الآن يُجلب من الخاصية الموجودة في الموديل
    current_balance = 0.0

    if supplier_id:
        selected_supplier = Supplier.query.get(supplier_id)
        if selected_supplier:
            # جلب الكشوفات باستخدام العلاقة المحددة في الموديل (statements)
            statements = selected_supplier.statements.order_by(SupplierStatement.created_at.desc()).all()
            # جلب الرصيد باستخدام الـ property الموجود في الموديل
            current_balance = selected_supplier.balance

    return render_template(
        'admin/statement.html',
        all_suppliers=all_suppliers,
        selected_supplier=selected_supplier,
        statements=statements,
        current_balance=current_balance
    )
