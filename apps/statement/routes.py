from flask import render_template, make_response
from weasyprint import HTML # تحتاج تثبيت: pip install weasyprint

@statement_blueprint.route('/api/statement/report/pdf', methods=['GET'])
@login_required
def export_report_pdf():
    try:
        # 1. جلب البيانات (استيراد محلي لتجنب الانهيار)
        from apps.models.statement_db import SupplierStatement
        data = SupplierStatement.query.all() # أو الفلتر الخاص بك
        
        # 2. تجهيز الـ HTML
        rendered = render_template('pdf_template.html', report_data=data)
        
        # 3. تحويل HTML إلى PDF مباشرة في الذاكرة
        pdf = HTML(string=rendered).write_pdf()
        
        # 4. إعداد الرد (Response)
        response = make_response(pdf)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = 'inline; filename=statement.pdf'
        
        return response
        
    except Exception as e:
        return f"❌ خطأ أثناء توليد التقرير: {str(e)}", 500
