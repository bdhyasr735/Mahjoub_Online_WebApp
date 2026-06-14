# 📂 apps/mahjoub_bridge/routes.py
import os
from flask import Blueprint, render_template, request, jsonify
from apps.utils.bridge_engine import QumraBridgeEngine

# 1. تحديد مسار القوالب بالنسبة لموقع هذا الملف
base_dir = os.path.dirname(os.path.abspath(__file__))
template_path = os.path.join(base_dir, 'templates')

# 2. تعريف الـ Blueprint مع إعطائه المسار الدقيق للقوالب
bridge_bp = Blueprint('mahjoub_bridge', __name__, template_folder='templates')

@bridge_bp.route('/dashboard', methods=['GET'])
def dashboard():
    # الآن Flask سيعرف أن يبحث داخل مجلد templates الخاص بهذا الـ Blueprint
    # والمسار هو admin/bridge_dashboard.html
    return render_template('admin/bridge_dashboard.html')

@bridge_bp.route('/api/search', methods=['GET'])
def api_search():
    engine = QumraBridgeEngine()
    query = request.args.get('q', '')
    return jsonify({"products": engine.get_data(query)})

@bridge_bp.route('/sync', methods=['POST'])
def sync():
    engine = QumraBridgeEngine()
    success = engine.sync_all_data()
    return jsonify({"status": "success" if success else "error"})
