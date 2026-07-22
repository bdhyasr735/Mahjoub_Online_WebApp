# coding: utf-8
# 📂 apps/suppliers_dashboard/routes/ai_routes.py

from flask import Blueprint, request, jsonify
from flask_login import login_required
import requests
import traceback
from config import Config

# ✅ تعريف الـ Blueprint
ai_bp = Blueprint(
    'ai_bp',
    __name__,
    template_folder='templates'
)


# ============================================================
# ✅ مساعد DeepSeek AI
# ============================================================
@ai_bp.route('/api/ask-ai', methods=['POST'])
@login_required
def ask_ai():
    """
    واجهة API للتواصل مع DeepSeek AI
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
        if not Config.DEEPSEEK_API_KEY:
            return jsonify({
                'success': False,
                'error': 'مفتاح DeepSeek غير موجود'
            }), 500
        
        # ✅ إرسال الطلب إلى DeepSeek
        response = requests.post(
            Config.DEEPSEEK_API_URL,
            headers={
                'Authorization': f'Bearer {Config.DEEPSEEK_API_KEY}',
                'Content-Type': 'application/json'
            },
            json={
                'model': Config.DEEPSEEK_MODEL,
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
            print(f"❌ خطأ في DeepSeek API: {response.status_code} - {response.text}")
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
        print(f"❌ خطأ في طلب DeepSeek: {e}")
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
