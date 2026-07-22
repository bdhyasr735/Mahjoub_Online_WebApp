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

# ✅ مفتاح OpenRouter
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY', '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')
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# ✅ قائمة النماذج المجانية (سيتم تجربتها تلقائياً)
FREE_MODELS = [
    'meta-llama/llama-3-8b-instruct',
    'google/gemma-2-9b-it',
    'microsoft/phi-3-mini-128k-instruct',
    'qwen/qwen-2.5-7b-instruct',
    'mistralai/mistral-7b-instruct-v0.1'
]


# ============================================================
# ✅ دالة تجربة النماذج تلقائياً
# ============================================================
def try_models(question, max_tokens=2048, temperature=0.7):
    """
    تجربة النماذج واحداً تلو الآخر حتى يعمل أحدهم
    """
    last_error = None
    
    for model in FREE_MODELS:
        try:
            print(f"🔄 [AI]: جاري تجربة النموذج: {model}")
            
            response = requests.post(
                OPENROUTER_API_URL,
                headers={
                    'Authorization': f'Bearer {OPENROUTER_API_KEY}',
                    'Content-Type': 'application/json',
                    'HTTP-Referer': 'https://mahjoub-online-webapp-j9ef.onrender.com',
                    'X-Title': 'Mahjoub Online'
                },
                json={
                    'model': model,
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
                        {'role': 'user', 'content': question}
                    ],
                    'max_tokens': max_tokens,
                    'temperature': temperature
                },
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"✅ [AI]: النموذج {model} يعمل بنجاح!")
                return {
                    'success': True,
                    'model': model,
                    'answer': response.json().get('choices', [{}])[0].get('message', {}).get('content', '')
                }
            else:
                print(f"⚠️ [AI]: النموذج {model} فشل (HTTP {response.status_code})")
                last_error = f"النموذج {model} فشل (HTTP {response.status_code})"
                
        except Exception as e:
            print(f"⚠️ [AI]: النموذج {model} فشل: {str(e)}")
            last_error = str(e)
            continue
    
    return {
        'success': False,
        'error': f'جميع النماذج فشلت. آخر خطأ: {last_error}'
    }


# ============================================================
# ✅ مسار اختبار الاتصال الديناميكي
# ============================================================
@ai_bp.route('/api/test-ai', methods=['GET'])
@login_required
def test_ai():
    """
    مسار اختبار للتحقق من النماذج المتاحة
    """
    results = []
    working_model = None
    
    for model in FREE_MODELS:
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
                    'model': model,
                    'messages': [
                        {'role': 'system', 'content': 'أنت مساعد مفيد.'},
                        {'role': 'user', 'content': 'مرحباً'}
                    ],
                    'max_tokens': 10
                },
                timeout=10
            )
            
            results.append({
                'model': model,
                'status_code': response.status_code,
                'working': response.status_code == 200
            })
            
            if response.status_code == 200 and not working_model:
                working_model = model
                
        except Exception as e:
            results.append({
                'model': model,
                'error': str(e),
                'working': False
            })
    
    return jsonify({
        'working_model': working_model,
        'results': results,
        'message': f"✅ النموذج العامل: {working_model}" if working_model else "❌ لا يوجد نموذج عامل"
    })


# ============================================================
# ✅ مساعد OpenRouter AI (ديناميكي)
# ============================================================
@ai_bp.route('/api/ask-ai', methods=['POST'])
@login_required
def ask_ai():
    """
    واجهة API للتواصل مع OpenRouter (تغير النموذج تلقائياً)
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
        
        # ✅ تجربة النماذج تلقائياً
        result = try_models(
            question,
            max_tokens=Config.DEEPSEEK_MAX_TOKENS,
            temperature=Config.DEEPSEEK_TEMPERATURE
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'answer': result['answer'],
                'model_used': result['model']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'فشلت جميع النماذج')
            }), 500
            
    except Exception as e:
        print(f"❌ خطأ غير متوقع في AI: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================================
# ✅ مسار للحصول على النموذج العامل (للواجهة)
# ============================================================
@ai_bp.route('/api/active-model', methods=['GET'])
@login_required
def get_active_model():
    """
    إرجاع النموذج النشط حالياً
    """
    return jsonify({
        'model': Config.OPENROUTER_MODEL,
        'available_models': FREE_MODELS
    })
