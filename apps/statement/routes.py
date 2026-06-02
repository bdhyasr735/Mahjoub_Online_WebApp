from flask import render_template, make_response # أضف make_response

@statement_blueprint.route('/api/statement/report/pdf', methods=['GET'])
@login_required
def export_report_pdf():
    try:
        # ... (نفس الكود الخاص بك لجلب البيانات) ...
        rendered = render_template('pdf_template.html', report_data=data)
        
        # إذا كنت تستخدم pdfkit للتحويل:
        # pdf = pdfkit.from_string(rendered, False)
        # response = make_response(pdf)
        # response.headers['Content-Type'] = 'application/pdf'
        # return response
        
        return rendered # مؤقتاً للتأكد من أن البيانات تصل للصفحة
    except Exception as e:
        return jsonify({'error': str(e)}), 500
