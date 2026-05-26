# coding: utf-8
# 📂 apps/statement/routes.py

from flask import render_template, request, jsonify
from flask_login import login_required
from apps.statement import statement_blueprint
from apps.models.supplier_db import Supplier
from apps.utils.report_generator import ReportGenerator  # استدعاء محرك التقارير المركزي
from sqlalchemy import or_
from datetime import datetime

@statement_blueprint.route('/view', methods=['GET'])
@login_required
def view_statement():
    currencies = ['USD', 'YER', 'SAR'] 
    return render_template('admin/statement.html', currencies=currencies)


# 1. البحث الذكي المتوافق بالكامل مع متطلبات الـ Select2 في الواجهة
@statement_blueprint.route('/api/suppliers/search', methods=['GET'])
@login_required
def api_search_suppliers():
    term = request.args.get('q', '')
    if not term:
        return jsonify({"results": []})

    try:
        # تم تنظيف الفلتر من حقل 'store_name' لحل مشكلة الـ AttributeError نهائياً
        suppliers = Supplier.query.filter(or_(
            Supplier.trade_name.ilike(f'%{term}%'),
            Supplier.owner_name.ilike(f'%{term}%'),
            Supplier.sovereign_id.ilike(f'%{term}%')
        )).limit(15).all()
        
        # استخدام getattr لضمان عدم توقف النظام حتى لو غاب أحد الحقول برمجياً
        results = [
            {
                'id': s.id, 
                'text': f"{getattr(s, 'trade_name', '---')} (المالك: {getattr(s, 'owner_name', '---')}) - المعرف: {getattr(s, 'sovereign_id', '---')}"
            } for s in suppliers
        ]
        return jsonify({"results": results})

    except Exception as e:
        # طباعة الخطأ في سجلات Railway لمتابعة جودة الاستعلام والتحقق اللحظي
        print(f"❌ Error during supplier search: {str(e)}")
        return jsonify({"results": [], "error": "حدث خطأ داخلي أثناء استعلام قاعدة البيانات"}), 500


# 2. جلب كشف الحساب الشامل والتقارير المالي عبر استدعاء الـ ReportGenerator
@statement_blueprint.route('/api/statement/report', methods=['GET'])
@login_required
def api_get_report():
    s_id = request.args.get('id')
    curr = request.args.get('currency', 'ALL')
    start_str = request.args.get('start')
    end_str = request.args.get('end')

    if not s_id:
        return jsonify({'error': 'يرجى تحديد المورد أولاً'}), 400

    supplier = Supplier.query.get(s_id)
    if not supplier: 
        return jsonify({'error': 'المورد غير موجود بالشرائح الحالية'}), 404

    # تحويل نصوص التواريخ القادمة من daterangepicker إلى كائنات datetime متوافقة مع قاعدة البيانات
    start_date = None
    end_date = None
    
    try:
        if start_str:
            start_date = datetime.strptime(start_str, '%Y-%m-%d').replace(hour=0, minute=0, second=0)
        if end_str:
            end_date = datetime.strptime(end_str, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
    except ValueError:
        return jsonify({'error': 'صيغة التاريخ غير صحيحة'}), 400

    # أ. استخراج الحركات التفصيلية للمورد من قاعدة البيانات عبر المحرك المركزي
    statements = ReportGenerator.get_detailed_transactions(
        supplier_id=supplier.id, 
        currency=curr, 
        start_date=start_date, 
        end_date=end_date
    )

    # ب. حساب صافي أرباح المنصة المرتبطة بالمورد والمحفظة عبر المحرك المركزي
    total_profit = ReportGenerator.calculate_net_profit(
        currency=curr, 
        start_date=start_date, 
        end_date=end_date
    )

    # ج. تجميع وإرسال البيانات بصيغة JSON النهائية لتغذية جدول الواجهة الفورية
    return jsonify({
        'summary': {
            'total_debit': float(sum(s.debit for s in statements)),
            'total_credit': float(sum(s.credit for s in statements)),
            'net_balance': float(sum(s.credit for s in statements) - sum(s.debit for s in statements)),
            'total_profit': float(total_profit)
        },
        'details': [{
            'date': s.created_at.strftime('%Y-%m-%d %H:%M') if s.created_at else '---',
            'desc': getattr(s, 'description', getattr(s, 'desc', '---')) or '---',
            # 👇 التعديل الوقائي هنا: جلب رقم المرجع بشكل آمن تماماً عبر getattr لمنع الانهيار
            'ref': getattr(s, 'reference_number', getattr(s, 'ref', '---')) or '---',
            'currency': getattr(s, 'currency', 'USD'),
            'debit': float(s.debit or 0),
            'credit': float(s.credit or 0),
            'balance': float(s.running_balance or 0)
        } for s in statements]
    })
