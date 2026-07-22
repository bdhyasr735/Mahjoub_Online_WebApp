# coding: utf-8
# 📂 apps/suppliers_dashboard/routes/ai_routes.py

from flask import Blueprint, request, jsonify
from flask_login import login_required
import requests
import traceback
import os
from config import Config

# ✅ تعريف الـ Blueprint
ai_bp = Blueprint(
    'ai_bp',
    __name__,
    template_folder='templates'
)

# ✅ مفتاح OpenRouter (مع قيمة افتراضية)
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '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')
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# ❌ تم حذف هذا السطر لأنه موجود في config.py


# ============================================================
# ✅ مسار اختبار الاتصال بـ OpenRouter
# ============================================================
@ai_bp.route('/api/test-ai', methods=['GET'])
@login_required
def test_ai():
    """
    مسار اختبار للتحقق من اتصال OpenRouter
    """
    result = {
        'api_key_exists': bool(OPENROUTER_API_KEY),
        'api_key_preview': OPENROUTER_API_KEY[:15] + '...' if OPENROUTER_API_KEY else '❌ غير موجود',
        'api_url': OPENROUTER_API_URL,
        'model': Config.OPENROUTER_MODEL,
        'test_result': None
    }
    
    if not OPENROUTER_API_KEY:
        result['error'] = 'مفتاح OpenRouter غير موجود'
        return jsonify(result), 500
    
    try:
        response = requests.post(
            OPENROUTER_API_URL,
            headers={
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://mahjoub-online-webapp-j9ef.onrender.com',
                'X-Title': 'Mahjoub Online'
            },
            json={
                'model': Config.OPENROUTER_MODEL,
                'messages': [
                    {'role': 'system', 'content': 'أنت مساعد مفيد.'},
                    {'role': 'user', 'content': 'مرحباً، قل لي كلمة واحدة فقط: مرحباً'}
                ],
                'max_tokens': 50,
                'temperature': 0.5
            },
            timeout=15
        )
        
        result['status_code'] = response.status_code
        result['test_result'] = response.text[:500]
        
        if response.status_code == 200:
            result['success'] = True
            data = response.json()
            result['reply'] = data.get('choices', [{}])[0].get('message', {}).get('content', 'لا يوجد رد')
        else:
            result['success'] = False
            result['error'] = f'خطأ {response.status_code}'
            
    except requests.exceptions.Timeout:
        result['success'] = False
        result['error'] = 'انتهى وقت الانتظار'
    except Exception as e:
        result['success'] = False
        result['error'] = str(e)
    
    return jsonify(result)


# ============================================================
# ✅ مساعد OpenRouter AI
# ============================================================
@ai_bp.route('/api/ask-ai', methods=['POST'])
@login_required
def ask_ai():
    """
    واجهة API للتواصل مع OpenRouter (نماذج مجانية متعددة)
    """
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': 'السؤال مطلوب'
            }), 400
        
        # ✅ التحقق من وجود مفتاح API
        if not OPENROUTER_API_KEY:
            return jsonify({
                'success': False,
                'error': 'مفتاح OpenRouter غير موجود'
            }), 500
        
        # ✅ إرسال الطلب إلى OpenRouter
        response = requests.post(
            OPENROUTER_API_URL,
            headers={
                'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                'Content-Type': 'application/json',
                'HTTP-Referer': 'https://mahjoub-online-webapp-j9ef.onrender.com',
                'X-Title': 'Mahjoub Online'
            },
            json={
                'model': Config.OPENROUTER_MODEL,
                'messages': [
                    {
                        'role': 'system',
                        'content': """أنت مساعد ذكي لمتجر محجوب أونلاين. مهمتك مساعدة الموردين في:
1. تحسين مبيعاتهم
2. تسويق منتجاتهم
3. إدارة المخزون
4. فهم التحليلات
5. نصائح لتطوير المتجر
كن ودوداً، محترفاً، ومفيداً. استخدم اللغة العربية الفصحى."""
                    },
                    {
                        'role': 'user',
                        'content': question
                    }
                ],
                'max_tokens': Config.DEEPSEEK_MAX_TOKENS,
                'temperature': Config.DEEPSEEK_TEMPERATURE
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            answer = result.get('choices', [{}])[0].get('message', {}).get('content', 'عذراً، لم أستطع معالجة طلبك.')
            answer = answer.strip()
            
            return jsonify({
                'success': True,
                'answer': answer
            })
        else:
            print(f"❌ خطأ في OpenRouter API: {response.status_code} - {response.text}")
            return jsonify({
                'success': False,
                'error': 'خطأ في الاتصال بالذكاء الاصطناعي'
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({
            'success': False,
            'error': 'انتهى وقت الانتظار، يرجى المحاولة مرة أخرى'
        }), 408
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ في طلب OpenRouter: {e}")
        return jsonify({
            'success': False,
            'error': 'حدث خطأ في الاتصال'
        }), 500
    except Exception as e:
        print(f"❌ خطأ غير متوقع في AI: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
