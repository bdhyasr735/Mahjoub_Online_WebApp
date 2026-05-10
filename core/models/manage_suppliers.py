# core/models/manage_suppliers.py
from flask import request, jsonify
from flask_login import login_required
from admin_panel import admin_bp  # استدعاء البلوبرنت من مجلد الإدارة
from .suppliers_logic import SupplierLogic 
# تأكد من وجود ملف auth.py داخل admin_panel يحتوي على admin_required
# إذا لم يوجد، استخدم login_required فقط مؤقتاً
try:
    from admin_panel.auth import admin_required 
except ImportError:
    admin_required = login_required 

# --- 1. محرك البحث الذكي ---
@admin_bp.route('/api/search-suppliers')
@login_required
@admin_required
def api_search_suppliers():
    q = request.args.get('q', '').strip()
    filters = {
        'province': request.args.get('province', '').strip(),
        'district': request.args.get('district', '').strip(),
        'tier': request.args.get('tier', '').strip(),
        'status': request.args.get('status', '').strip()
    }
    
    # استدعاء المنطق من العقل المدبر
    results = SupplierLogic.search_suppliers(q, filters)
    
    return jsonify({
        "status": "success",
        "count": len(results),
        "suppliers": [s.to_dict() for s in results]
    })

# --- 2. محرك جلب التفاصيل الكاملة ---
@admin_bp.route('/api/get-supplier-full-details/<int:s_id>')
@login_required
@admin_required
def get_supplier_full_details(s_id):
    data = SupplierLogic.get_full_details(s_id)
    if data:
        return jsonify(data)
    return jsonify({"status": "error", "message": "الكيان غير موجود"}), 404

# --- 3. محرك تحديث البيانات والأرصدة ---
@admin_bp.route('/api/update-sovereign-data/<int:s_id>', methods=['POST'])
@login_required
@admin_required
def update_sovereign_data(s_id):
    success, message = SupplierLogic.update_supplier_data(s_id, request.get_json())
    return jsonify({"status": "success" if success else "error", "message": message})

# --- 4. محرك حذف الكيان ---
@admin_bp.route('/api/delete-sovereign-entity/<int:s_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_entity(s_id):
    success, message = SupplierLogic.delete_entity(s_id)
    return jsonify({"status": "success" if success else "error", "message": message})
