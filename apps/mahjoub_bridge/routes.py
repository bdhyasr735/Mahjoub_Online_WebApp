# coding: utf-8
# 📂 apps/mahjoub_bridge/routes.py

from flask import Blueprint, render_template, request, jsonify
from apps.utils.bridge_engine import QumraBridgeEngine
import traceback

# تعريف الـ Blueprint
# ملاحظة: إذا كان تطبيقك يضيف بادئة (Prefix) للمسارات عند تسجيل الـ Blueprint في apps/__init__.py،
# يجب أن تحذف كلمة 'bridge/' من داخل المسارات هنا لتجنب التكرار.
bridge_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@bridge_bp.route('/bridge/dashboard', methods=['GET'])
def dashboard():
    """عرض صفحة لوحة التحكم."""
    return render_template('admin/bridge_dashboard.html')

@bridge_bp.route('/bridge/api/search', methods=['GET'])
def api_search():
    """API لجلب البيانات بتنسيق JSON."""
    try:
        search = request.args.get('q', '', type=str)
        per_page = request.args.get('per_page', 9999, type=int)
        
        engine = QumraBridgeEngine()
        data = engine.fetch_products(search_term=search, page=1, per_page=per_page)
        
        return jsonify(data)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@bridge_bp.route('/bridge/sync-now', methods=['POST'])
def sync_now():
    """إعادة مزامنة البيانات من المصدر مع معالجة أخطاء تفصيلية."""
    try:
        engine = QumraBridgeEngine()
        print("🔄 [System] Starting sync...")
        
        success = engine.sync_all_data()
        
        if success:
            return jsonify({"status": "success", "message": "تم تحديث البيانات بنجاح"})
        else:
            return jsonify({"status": "error", "message": "فشل الاتصال بالمصدر (راجع مفتاح الـ API)"}), 500
            
    except Exception as e:
        print(f"❌ [Error] Sync failed: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "خطأ في السيرفر: " + str(e)}), 500
