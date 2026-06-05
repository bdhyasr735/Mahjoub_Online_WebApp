# apps/api/search.py
from flask import Blueprint, request, jsonify
from apps.models.supplier_db import Supplier

# تم التعديل هنا ليطابق ما هو مسجل في __init__.py
api_search = Blueprint('api_search', __name__)

@api_search.route('/api/search', methods=['GET']) # تم التعديل أيضاً هنا
def search_suppliers():
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({"results": []})

    suppliers = Supplier.query.filter(
        (Supplier.search_name.ilike(f'%{query}%')) | 
        (Supplier.search_phone.ilike(f'%{query}%'))
    ).limit(10).all()

    results = []
    for s in suppliers:
        results.append({
            "id": s.id,
            "name": s.trade_name, 
            "phone": s.owner_phone
        })

    return jsonify({"results": results})
