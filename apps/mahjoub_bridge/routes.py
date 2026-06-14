# coding: utf-8
# 📂 apps/mahjoub_bridge/routes.py

from flask import Blueprint, render_template, request, jsonify
from apps.utils.bridge_engine import QumraBridgeEngine

# تعريف الـ Blueprint مع تحديد مكان القوالب
bridge_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@bridge_bp.route('/bridge/dashboard', methods=['GET'])
def dashboard():
    """
    عرض صفحة لوحة التحكم الخاصة بالمنتجات.
    """
    return render_template('admin/bridge_dashboard.html')

@bridge_bp.route('/bridge/api/search', methods=['GET'])
def api_search():
    """
    API لجلب البيانات: يستقبل البحث والترقيم ويرد بـ JSON.
    """
    search = request.args.get('q', '', type=str)
    # نستخدم قيمة per_page التي تأتي من الفرونت، إذا لم تتوفر نستخدم 9999 لجلب الكل
    per_page = request.args.get('per_page', 9999, type=int)
    
    engine = QumraBridgeEngine()
    data = engine.fetch_products(search_term=search, page=1, per_page=per_page)
    
    return jsonify(data)

@bridge_bp.route('/bridge/sync-now', methods=['POST'])
def sync_now():
    """
    إعادة مزامنة البيانات من المصدر (قمرة).
    """
    engine = QumraBridgeEngine()
    success = engine.sync_all_data()
    
    if success:
        return jsonify({"status": "success", "message": "تم تحديث البيانات بنجاح"})
    else:
        return jsonify({"status": "error", "message": "فشل الاتصال بالمصدر"}), 500
