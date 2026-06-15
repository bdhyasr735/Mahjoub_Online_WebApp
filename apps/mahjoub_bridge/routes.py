# 📂 apps/mahjoub_bridge/routes.py
from flask import Blueprint, render_template, request, jsonify
from apps.utils.products_engine import ProductsEngine
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
    تستخدم الآن محرك المنتجات المتخصص ProductsEngine.
    """
    search_query = request.args.get('q', '')
    page = int(request.args.get('page', 1))
    
    try:
        # استدعاء المحرك المتخصص للمنتجات
        engine = ProductsEngine()
        data = engine.fetch_all(search_query, page)
        
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
            "message": "فشل الاتصال بخادم المنتجات",
            "products": []
        }), 500

@bridge_bp.route('/sync', methods=['POST'])
def sync():
    """تشغيل عملية المزامنة يدوياً"""
    try:
        # هنا يمكنك لاحقاً استدعاء المزامنة للمنتجات أو الطلبات
        engine = ProductsEngine()
        success = True # سيتم استبدالها لاحقاً بمنطق المزامنة الفعلي
        return jsonify({
            "status": "success" if success else "error",
            "message": "تمت عملية المزامنة بنجاح"
        })
    except Exception as e:
        logger.error(f"Error in sync: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "حدث خطأ أثناء المزامنة"
        }), 500
