# 📂 apps/api/search.py
from flask import Blueprint, request, jsonify
from apps.models.supplier_db import Supplier

# تم التعديل ليطابق ما هو مسجل في المصنع __init__.py
api_search = Blueprint('api_search', __name__)

# تعديل المسار إلى '/search' فقط، لأن المصنع يضيف '/api' تلقائياً
@api_search.route('/search', methods=['GET']) 
def search_suppliers():
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({"results": []})

    # البحث باستخدام ilike
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
