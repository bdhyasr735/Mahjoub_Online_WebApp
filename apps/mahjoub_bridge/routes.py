# 📂 apps/mahjoub_bridge/routes.py
from flask import Blueprint, render_template, request, jsonify
from apps.utils.bridge_engine import QumraBridgeEngine
import logging

# إعداد سجل الأخطاء للمتابعة
logger = logging.getLogger(__name__)

bridge_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@bridge_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """عرض لوحة التحكم الخاصة بالجسر"""
    return render_template('admin/bridge_dashboard.html')

@bridge_bp.route('/api/search', methods=['GET'])
def api_search():
    """
    نقطة اتصال للبحث المباشر:
    1. تستقبل طلب البحث (q) ورقم الصفحة (page).
    2. تستدعي المحرك لجلب البيانات بناءً على المتغيرات.
    3. تعيد النتائج بتنسيق JSON.
    """
    search_query = request.args.get('q', '')
    # التأكد من استقبال رقم الصفحة وتحويله لعدد صحيح، والافتراضي هو 1
    page = int(request.args.get('page', 1))
    
    try:
        # استدعاء المحرك المطور الذي يدعم الآن المتغيرات (query & page)
        engine = QumraBridgeEngine()
        data = engine.fetch_products_from_qumra(search_query, page)
        
        return jsonify({
            "status": "success",
            "products": data,
            "count": len(data),
            "page": page
        })
    except Exception as e:
        logger.error(f"Error in api_search: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "فشل الاتصال بخادم المتجر المصدر",
            "products": []
        }), 500

@bridge_bp.route('/sync', methods=['POST'])
def sync():
    """تشغيل عملية المزامنة يدوياً عند الطلب"""
    try:
        engine = QumraBridgeEngine()
        # التأكد من وجود الدالة قبل استدعائها
        success = engine.sync_all_data() if hasattr(engine, 'sync_all_data') else False
        return jsonify({
            "status": "success" if success else "error",
            "message": "تمت عملية المزامنة بنجاح" if success else "فشلت عملية المزامنة"
        })
    except Exception as e:
        logger.error(f"Error in sync: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "حدث خطأ أثناء المزامنة"
        }), 500
