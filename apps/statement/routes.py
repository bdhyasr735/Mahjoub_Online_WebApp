# coding: utf-8
from flask import render_template, request, flash
from flask_login import login_required
from apps.statement import statement_blueprint
from apps.models.supplier_db import Supplier
from apps.models.wallet_db import WalletTransaction 

@statement_blueprint.route('/view', methods=['GET'])
@login_required
def view_statement():
    # 1. جلب كل الموردين
    all_suppliers = Supplier.query.all()
    
    # 2. جلب معرف المورد من الرابط
    supplier_id = request.args.get('supplier_id')
    selected_supplier = None
    statements = []
    balances = {'SAR': 0.0, 'YER': 0.0, 'USD': 0.0}

    if supplier_id:
        try:
            # جلب المورد
            selected_supplier = Supplier.query.get(supplier_id)
            
            if selected_supplier:
                # 3. جلب الحركات (تم وضع شرط مبدئي للتأكد من وجود الحقل)
                statements = WalletTransaction.query.filter_by(supplier_id=supplier_id).order_by(WalletTransaction.created_at.desc()).all()
                
                # 4. جلب الأرصدة بطريقة آمنة لتفادي الـ 500 Error
                # إذا لم يجد الحقل، سيعود بـ 0.0 بدلاً من التسبب بانهيار السيرفر
                balances = {
                    'SAR': getattr(selected_supplier, 'sar_balance', 0.0) or 0.0,
                    'YER': getattr(selected_supplier, 'yer_balance', 0.0) or 0.0,
                    'USD': getattr(selected_supplier, 'usd_balance', 0.0) or 0.0
                }
        except Exception as e:
            # في حال حدوث خطأ، سنقوم بطباعته في السيرفر دون إيقافه
            print(f"Error in view_statement: {e}")
            flash(f"حدث خطأ أثناء جلب البيانات: {str(e)}", "danger")

    return render_template(
        'admin/statement.html',
        all_suppliers=all_suppliers,
        selected_supplier=selected_supplier,
        statements=statements,
        balances=balances
    )
