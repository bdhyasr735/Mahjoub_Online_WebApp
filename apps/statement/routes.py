# coding: utf-8
# 📂 apps/statement/routes.py

from flask import render_template, request, jsonify, make_response
from flask_login import login_required
from apps.statement import statement_blueprint
from apps.models.supplier_db import Supplier
from apps.utils.report_generator import ReportGenerator
from sqlalchemy import or_
from datetime import datetime

@statement_blueprint.route('/view', methods=['GET'])
@login_required
def view_statement():
    currencies = ['USD', 'YER', 'SAR']
    return render_template('admin/statement.html', currencies=currencies)

# مسار لجلب خلاصة أرصدة كافة المحافظ (الملخص الشامل للمنصة)
@statement_blueprint.route('/api/statement/summary_all', methods=['GET'])
@login_required
def api_get_all_summary():
    curr = request.args.get('currency', 'ALL')
    summary_data = ReportGenerator.get_all_wallets_summary(currency=curr)
    return jsonify({'results': summary_data})

# 1. البحث الذكي المتوافق بالكامل
@statement_blueprint.route('/api/suppliers/search', methods=['GET'])
@login_required
def api_search_suppliers():
    term = request.args.get('q', '')
    if not term:
        return jsonify({"results": []})

    try:
        suppliers = Supplier.query.filter(or_(
            Supplier.trade_name.ilike(f'%{term}%'),
            Supplier.owner_name.ilike(f'%{term}%'),
            Supplier.sovereign_id.ilike(f'%{term}%')
        )).limit(15).all()
        
        results = [{
            'id': s.id, 
            'text': f"{getattr(s, 'trade_name', '---')} (المالك: {getattr(s, 'owner_name', '---')}) - WEL: {getattr(s, 'sovereign_id', '---')}"
        } for s in suppliers]
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"results": [], "error": "حدث خطأ داخلي"}), 500

# 2. جلب كشف الحساب التفصيلي
@statement_blueprint.route('/api/statement/report', methods=['GET'])
@login_required
def api_get_report():
    s_id = request.args.get('id', 'ALL')
    curr = request.args.get('currency', 'ALL')
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    try:
        start_date = datetime.strptime(start_str, '%Y-%m-%d') if start_str else None
        end_date = datetime.strptime(end_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59) if end_str else None
    except ValueError:
        return jsonify({'error': 'صيغة التاريخ غير صحيحة'}), 400

    statements = ReportGenerator.get_detailed_transactions(s_id, curr, start_date, end_date)
    total_profit = ReportGenerator.calculate_net_profit(curr, start_date, end_date)

    return jsonify({
        'summary': {
            'total_debit': float(sum(s.debit or 0 for s in statements)),
            'total_credit': float(sum(s.credit or 0 for s in statements)),
            'net_balance': float(sum(s.credit or 0 for s in statements) - sum(s.debit or 0 for s in statements)),
            'total_profit': float(total_profit)
        },
        'details': [{
            'date': s.created_at.strftime('%Y-%m-%d %H:%M'),
            'desc': getattr(s, 'description', '---'),
            'ref': '---',  # تم استبدال reference_number بقيمة ثابتة لعدم وجود العمود
            'currency': getattr(s, 'currency', 'USD'),
            'debit': float(s.debit or 0),
            'credit': float(s.credit or 0),
            'balance': float(s.running_balance or 0)
        } for s in statements]
    })

# 3. مسار عرض التقرير (يفتح كصفحة طباعة/تنزيل)
@statement_blueprint.route('/api/statement/report/pdf', methods=['GET'])
@login_required
def export_report_pdf():
    s_id = request.args.get('supplier_id', 'ALL')
    curr = request.args.get('currency', 'ALL')
    start_str = request.args.get('start_date')
    end_str = request.args.get('end_date')
    
    start_date = datetime.strptime(start_str, '%Y-%m-%d') if start_str else None
    end_date = datetime.strptime(end_str, '%Y-%m-%d') if end_str else None

    wallet_code = "---"
    supplier_name = "تقرير شامل للمنصة"
    
    if s_id and s_id != 'ALL':
        supplier = Supplier.query.get(s_id)
        if supplier:
            wallet_code = getattr(supplier, 'sovereign_id', '---')
            supplier_name = getattr(supplier, 'trade_name', '---')

    statements = ReportGenerator.get_detailed_transactions(s_id, curr, start_date, end_date)
    
    total_debit = sum(s.debit or 0 for s in statements)
    total_credit = sum(s.credit or 0 for s in statements)
    
    return render_template(
        'pdf_template.html',
        statements=statements,
        supplier_name=supplier_name,
        wallet_code=wallet_code,
        currency=curr,
        total_debit=total_debit,
        total_credit=total_credit,
        net_balance=total_credit - total_debit,
        start_date=start_str,
        end_date=end_str,
        generated_at=datetime.utcnow().strftime('%Y/%m/%d %H:%M')
    )
