# admin_panel/manage_suppliers.py
from flask import Blueprint, request, jsonify
from .suppliers_logic import SupplierLogic  # استدعاء العقل المدبر

# تعريف المحرك كبلوبرنت مستقل
admin_suppliers_bp = Blueprint('admin_suppliers', __name__)

@admin_suppliers_bp.route('/admin/api/supplier/approve/<int:sup_id>', methods=['POST'])
def approve(sup_id):
    """محرك التعميد: يستلم الطلب وينادي المنطق"""
    success, message = SupplierLogic.approve_supplier(sup_id)
    return jsonify({"status": "success" if success else "error", "message": message})

@admin_suppliers_bp.route('/admin/api/suppliers/search')
def search():
    """محرك البحث: يستلم الكلمات المفتاحية وينادي المنطق"""
    query = request.args.get('q', '').strip()
    status = request.args.get('status', '')
    results = SupplierLogic.search_suppliers(query, status)
    return jsonify([sup.to_dict() for sup in results])

@admin_suppliers_bp.route('/admin/api/supplier/<int:sup_id>/update', methods=['POST'])
def update(sup_id):
    """محرك التحديث: يستلم البيانات الجديدة وينادي المنطق"""
    data = request.json
    success, message = SupplierLogic.update_supplier_data(sup_id, data)
    return jsonify({"status": "success" if success else "error", "message": message})
