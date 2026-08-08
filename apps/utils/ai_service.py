from flask import Blueprint, render_template, request, jsonify
from apps.utils.ai_service import analyze_permissions_query

suppliers_permissions_bp = Blueprint('suppliers_permissions', __name__, template_folder='templates')

@suppliers_permissions_bp.route('/ai-check-permissions', methods=['POST'])
def ai_check_permissions():
    data = request.get_json()
    user_prompt = data.get('prompt', '')
    
    # استدعاء الذكاء الاصطناعي لمعالجة الطلب الخاص بالصلاحيات
    ai_response = analyze_permissions_query(user_prompt)
    
    return jsonify({
        'status': 'success',
        'result': ai_response
    })
