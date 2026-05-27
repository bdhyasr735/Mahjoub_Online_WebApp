# coding: utf-8
# 📂 apps/statement/routes.py - نظام التقارير والسيادة المالية

from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from apps.statement import statement_blueprint
from apps.models.supplier_db import Supplier
from apps.utils.report_generator import ReportGenerator
from sqlalchemy import or_
from datetime import datetime

# دالة مساعدة لتنظيف القيم القادمة من الـ Request
def get_clean_param(param_name, default='ALL'):
    val = request.args.get(param_name, default)
    return default if val in ['null', 'undefined', '', None] else val

@statement_blueprint.route('/view', methods=['GET'])
@login_required
def view_statement():
    currencies = ['USD', 'YER', 'SAR']
    return render_template('admin/statement.html', currencies=currencies)

# 1. البحث عن الموردين (محرك بحث ذكي)
@statement_blueprint.route('/api/suppliers/search', methods=['GET'])
@login_required
def api_search_suppliers():
    term = request.args.get('q', '')
    try:
        suppliers = Supplier.query.filter(or_(
            Supplier.trade_name.ilike(f'%{term}%'),
            Supplier.owner_name.ilike(f'%{term}%'),
            Supplier.sovereign_id.ilike(f'%{term}%')
        )).limit(15).all()
        
        results = [{
            'id': s.id, 
            'text': f"{getattr(s, 'trade_name', '---')} ({getattr(s, 'sovereign_id', '---')})"
        } for s in suppliers]
        return jsonify({"results": results})
    except Exception:
        return jsonify({"results": []}), 500

# 2. ملخص أرصدة كافة الموردين
@statement_blueprint.route('/api/statement/summary_all', methods=['GET'])
@login_required
def api_get_all_summary():
    curr = get_clean_param('currency')
    summary_data = ReportGenerator.get_all_wallets_summary(currency=curr)
    return jsonify({'results': summary_data})

# 3. تقرير كشف الحساب التفصيلي
@statement_blueprint.route('/api/statement/report', methods=['GET'])
@login_required
def api_get_report():
    try:
        s_id = get_clean_param('id')
        curr = get_clean_param('currency')
        start_str = request.args.get('start')
        end_str = request.args.get('end')

        start_date = datetime.strptime(start_str, '%Y-%m-%d') if start_str and start_str not in ['null', 'undefined', None] else None
        end_date = datetime.strptime(end_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59) if end_str and end_str not in ['null', 'undefined', None] else None

        statements = ReportGenerator.get_detailed_transactions(s_id, curr, start_date, end_date)
        
        if not statements:
            return jsonify({'summary': {'total_debit': 0, 'total_credit': 0, 'net_balance': 0, 'total_profit': 0}, 'details': []})

        total_profit = ReportGenerator.calculate_net_profit(curr, start_date, end_date)

        return jsonify({
            'summary': {
                'total_debit': float(sum(s.debit or 0 for s in statements)),
                'total_credit': float(sum(s.credit or 0 for s in statements)),
                'net_balance': float(sum(s.credit or 0 for s in statements) - sum(s.debit or 0 for s in statements)),
                'total_profit': float(total_profit or 0)
            },
            'details': [{
                'date': s.created_at.strftime('%Y-%m-%d'),
                'desc': getattr(s, 'description', '---'),
                'currency': getattr(s, 'currency', 'USD'),
                'debit': float(s.debit or 0),
                'credit': float(s.credit or 0),
                'balance': float(s.running_balance or 0)
            } for s in statements]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 4. تصدير التقارير (PDF) - تم تصحيح استدعاء render_template
@statement_blueprint.route('/api/statement/report/pdf', methods=['GET'])
@login_required
def export_report_pdf():
    try:
        s_id = get_clean_param('supplier_id')
        curr = get_clean_param('currency')
        # جلب البيانات اللازمة للتقرير
        data = ReportGenerator.get_detailed_transactions(s_id, curr)
        
        # تمرير البيانات كمتغير مسمى (report_data) لتجنب الخطأ السابق
        return render_template('pdf_template.html', report_data=data)
    except Exception as e:
        return jsonify({'error': f"PDF Generation failed: {str(e)}"}), 500
