# coding: utf-8
# 📂 apps/statement/routes.py
# ⚙️ محرك كشوفات الموردين المركزية - نظام محجوب أونلاين 2026

from flask import render_template, request, flash
from flask_login import login_required
from apps.statement import statement_blueprint
from sqlalchemy import or_

@statement_blueprint.route('/view', methods=['GET'])
@login_required
def view_statement():
    """
    عرض كشف حساب الموردين مع دعم الفلترة حسب العملة والتاريخ.
    تم نقل الاستيرادات إلى هنا لكسر حلقة الاستيراد الدائرية.
    """
    # الاستيراد داخل الدالة فقط - الحل السحري لإنهاء انهيار السيرفر
    from apps.models.supplier_db import Supplier
    from apps.models.statement_db import SupplierStatement

    q = request.args.get('q', '')
    currency = request.args.get('currency', 'ALL')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    selected_supplier = None
    statements = []

    # البحث عن المورد وتجهيز كشف الحساب
    if q:
        try:
            # البحث عن المورد
            selected_supplier = Supplier.query.filter(or_(
                Supplier.trade_name.ilike(f'%{q}%'),
                Supplier.owner_name.ilike(f'%{q}%'),
                Supplier.sovereign_id == q
            )).first()
            
            if selected_supplier:
                # إنشاء استعلام الكشف
                query = SupplierStatement.query.filter_by(supplier_id=selected_supplier.id)
                
                # تطبيق الفلاتر الإضافية
                if currency != 'ALL':
                    query = query.filter_by(currency=currency)
                if start_date:
                    query = query.filter(SupplierStatement.created_at >= start_date)
                if end_date:
                    query = query.filter(SupplierStatement.created_at <= end_date)
                
                # جلب البيانات مرتبة زمنياً
                statements = query.order_by(SupplierStatement.created_at.desc()).all()
            else:
                flash("لم يتم العثور على مورد بهذه البيانات.", "warning")
        
        except Exception as e:
            print(f"Error in view_statement: {e}")
            flash("حدث خطأ تقني أثناء تحميل الكشف.", "danger")
            statements = []

    return render_template(
        'admin/statement.html',
        selected_supplier=selected_supplier,
        statements=statements,
        currency_filter=currency,
        start_date=start_date,
        end_date=end_date
    )
