# coding: utf-8
# 📂 apps/mahjoub_bridge/routes.py

from flask import Blueprint, render_template, request, jsonify
from apps.utils.bridge_engine import QumraBridgeEngine
import traceback

# تعريف الـ Blueprint
bridge_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@bridge_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """
    لوحة التحكم:
    تعرض الصفحة الأولى للمنتجات.
    """
    search = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    engine = QumraBridgeEngine()
    # المحرك الآن يجلب البيانات مع الكمية (quantity) بفضل تحديثنا الأخير
    data = engine.fetch_products(search_term=search, page=page, per_page=per_page)
    
    return render_template('admin/bridge_dashboard.html', 
                           data=data, 
                           search=search)

@bridge_bp.route('/api/search', methods=['GET'])
def api_search():
    """
    مسار البحث اللحظي (API):
    يُستخدم بواسطة الـ JavaScript لجلب البيانات وتحديث الواجهة ديناميكياً.
    """
    search = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    engine = QumraBridgeEngine()
    data = engine.fetch_products(search_term=search, page=page, per_page=per_page)
    
    # إرجاع البيانات بتنسيق JSON نظيف لاستخدامه في تحديث الواجهة
    return jsonify(data)

@bridge_bp.route('/sync-now', methods=['POST'])
def sync_now():
    """
    المزامنة:
    تقوم بسحب كافة البيانات وتحديث الكاش.
    """
    try:
        engine = QumraBridgeEngine()
        success = engine.sync_all_data()
        
        if success:
            return jsonify({
                "status": "success", 
                "message": "تم تحديث كافة المنتجات بنجاح من النظام السيادي"
            })
        else:
            return jsonify({
                "status": "error", 
                "message": "فشل الاتصال: تأكد من مفتاح الربط والاتصال بالإنترنت"
            }), 500
        
    except Exception as e:
        print(f"❌ Sync Route Error: {traceback.format_exc()}")
        return jsonify({
            "status": "error", 
            "message": f"حدث خطأ: {str(e)}"
        }), 500
