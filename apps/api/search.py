# apps/api/search.py
from flask import Blueprint, request, jsonify
from apps.models.supplier_db import Supplier

# إنشاء "نقطة اتصال" (Blueprint) للبحث
search_bp = Blueprint('search_bp', __name__)

@search_bp.route('/api/search', methods=['GET'])
def search_suppliers():
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({"results": []})

    # البحث في الأعمدة التي أضفناها (search_name و search_phone)
    # نستخدم ilike للبحث عن جزء من الاسم أو الهاتف
    suppliers = Supplier.query.filter(
        (Supplier.search_name.ilike(f'%{query}%')) | 
        (Supplier.search_phone.ilike(f'%{query}%'))
    ).limit(10).all()

    results = []
    for s in suppliers:
        results.append({
            "id": s.id,
            "name": s.trade_name,  # الاسم التجاري المشفر
            "phone": s.owner_phone # الهاتف المشفر
        })

    return jsonify({"results": results})
