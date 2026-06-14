# coding: utf-8
# 📂 apps/mahjoub_bridge/routes.py

from flask import Blueprint, render_template, request, jsonify
from apps.utils.bridge_engine import QumraBridgeEngine
import traceback

bridge_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@bridge_bp.route('/dashboard', methods=['GET'])
def dashboard():
    """لوحة التحكم: تعرض البيانات مع دعم الترقيم واختيار عدد العناصر."""
    search = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int) # الافتراضي 10
    
    engine = QumraBridgeEngine()
    data = engine.fetch_products(search_term=search, page=page, per_page=per_page)
    
    return render_template('admin/bridge_dashboard.html', 
                           data=data, 
                           search=search)

@bridge_bp.route('/api/search', methods=['GET'])
def api_search():
    """مسار البحث اللحظي مع دعم الترقيم وحجم الصفحة."""
    search = request.args.get('q', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    engine = QumraBridgeEngine()
    data = engine.fetch_products(search_term=search, page=page, per_page=per_page)
    
    return jsonify(data)

@bridge_bp.route('/sync-now', methods=['POST'])
def sync_now():
    try:
        engine = QumraBridgeEngine()
        success = engine.sync_all_data()
        if success:
            return jsonify({"status": "success", "message": "تم التحديث بنجاح"})
        return jsonify({"status": "error", "message": "فشل الاتصال"}), 500
    except Exception:
        print(f"❌ Sync Error: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": "حدث خطأ تقني"}), 500
