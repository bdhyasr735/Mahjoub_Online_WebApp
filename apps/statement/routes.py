# coding: utf-8
# 📂 apps/statement/routes.py
# ⚙️ محرك كشوفات الموردين المركزية - نظام محجوب أونلاين 2026

from flask import render_template, request, flash
from flask_login import login_required
from apps.statement import statement_blueprint
from apps.utils.report_generator import ReportGenerator
from sqlalchemy import or_

@statement_blueprint.route('/view', methods=['GET'])
@login_required
def view_statement():
    """
    محرك عرض كشف حساب الموردين.
    تم استيراد Supplier محلياً لكسر حلقة الاستيراد الدائرية.
    """
    from apps.models.supplier_db import Supplier
    
    # 1. التقاط مدخلات البحث والفلترة
    q = request.args.get('q', '')
    currency = request.args.get('currency', 'ALL')
    report_type = request.args.get('report_type', 'detailed')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    selected_supplier = None
    statements = []

    # 2. منطق البحث الذكي
    if q:
        try:
            # البحث عن المورد عبر الاسم التجاري، اسم المالك، أو الرقم السيادي
            selected_supplier = Supplier.query.filter(or_(
                Supplier.trade_name.ilike(f'%{q}%'),
                Supplier.owner_name.ilike(f'%{q}%'),
                Supplier.sovereign_id == q
            )).first()
            
            # 3. جلب البيانات باستخدام محرك التقارير
            if selected_supplier:
                statements = ReportGenerator.get_detailed_transactions(
                    supplier_id=selected_supplier.id,
                    currency=currency,
                    start_date=start_date,
                    end_date=end_date
                ) or []
            else:
                flash("لم يتم العثور على مورد بهذه البيانات.", "warning")
        
        except Exception as e:
            print(f"Error in view_statement: {e}")
            flash("حدث خطأ تقني أثناء تحميل الكشف، يرجى المحاولة لاحقاً.", "danger")
            statements = []

    return render_template(
        'admin/statement.html',
        selected_supplier=selected_supplier,
        statements=statements,
        report_type=report_type,
        currency_filter=currency,
        start_date=start_date,
        end_date=end_date
    )
