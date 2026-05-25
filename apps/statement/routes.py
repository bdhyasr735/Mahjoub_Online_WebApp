# coding: utf-8
# 📂 apps/statement/routes.py
from flask import render_template
from flask_login import login_required
from apps.statement import statement_blueprint
from apps.models.statement_db import SupplierStatement
from apps.models.supplier_db import Supplier

@statement_blueprint.route('/view', defaults={'supplier_id': None})
@statement_blueprint.route('/view/<int:supplier_id>')
@login_required
def view_statement(supplier_id):
    # 1. جلب قائمة الموردين مرتبة أبجدياً لعرضها في قائمة البحث
    all_suppliers = Supplier.query.order_by(Supplier.trade_name.asc()).all()
    
    statements = []
    supplier = None
    
    # 2. تعريف هيكل الأرصدة للعملات الثلاث بشكل افتراضي (صفرية)
    balances = {'SAR': 0.0, 'YER': 0.0, 'USD': 0.0}

    # 3. إذا تم اختيار مورد، نجلب حركاته ونحسب أرصدته الفعلية
    if supplier_id:
        supplier = Supplier.query.get_or_404(supplier_id)
        
        # جلب جميع الحركات المالية الخاصة بهذا المورد
        statements = SupplierStatement.query.filter_by(supplier_id=supplier_id)\
                                           .order_by(SupplierStatement.created_at.desc()).all()
        
        # 4. حساب الأرصدة الفعلية لكل عملة (صافي الدائن والمدين)
        # النظام هنا محايد تماماً: لا يتم خصم أي عمولات إدارية
        for stmt in statements:
            if stmt.currency in balances:
                credit = float(stmt.credit or 0)
                debit = float(stmt.debit or 0)
                balances[stmt.currency] += (credit - debit)

    # 5. عرض الصفحة مع البيانات الصافية
    return render_template('admin/statement.html', 
                           statements=statements,
                           all_suppliers=all_suppliers,
                           selected_supplier=supplier,
                           balances=balances)
