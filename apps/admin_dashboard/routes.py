# coding: utf-8
from flask import render_template, request
from flask_login import login_required
from apps.statement import statement_blueprint
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import WalletTransaction # تأكد من استيراد الموديل الصحيح للحركات

@statement_blueprint.route('/view', methods=['GET'])
@login_required
def view_statement():
    # 1. جلب قائمة كل الموردين للقائمة المنسدلة
    all_suppliers = Supplier.query.all()
    
    # 2. جلب معرف المورد من الرابط
    supplier_id = request.args.get('supplier_id')
    selected_supplier = None
    statements = []
    balances = {'SAR': 0.0, 'YER': 0.0, 'USD': 0.0}

    if supplier_id:
        # جلب المورد المحدد
        selected_supplier = Supplier.query.get(supplier_id)
        
        if selected_supplier:
            # 3. جلب الحركات المالية لهذا المورد (بناءً على الكود أو الآيدي)
            # افترضت هنا أن الحركات مرتبطة بـ supplier_id في جدول الحركات
            statements = WalletTransaction.query.filter_by(supplier_id=supplier_id).order_by(WalletTransaction.created_at.desc()).all()
            
            # 4. حساب الأرصدة (تأكد أن حقول الأرصدة موجودة في الموديل الخاص بك)
            # إذا كان لديك جدول أرصدة منفصل، استبدل هذا الاستعلام بما يناسبه
            balances = {
                'SAR': selected_supplier.sar_balance or 0.0,
                'YER': selected_supplier.yer_balance or 0.0,
                'USD': selected_supplier.usd_balance or 0.0
            }

    return render_template(
        'admin/statement.html',
        all_suppliers=all_suppliers,
        selected_supplier=selected_supplier,
        statements=statements,
        balances=balances
    )
