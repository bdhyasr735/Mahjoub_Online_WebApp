# coding: utf-8
# 📂 apps/admin_Product/routes/products.py

import time
from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier

# ⚡ ذاكرة مؤقتة لتخزين المنتجات وتسريع البحث الفوري (تتحدث كل 60 ثانية)
_products_cache = {
    'data': None,
    'timestamp': 0
}
CACHE_TTL = 60  # مدة التخزين بالثواني

def get_cached_all_products():
    """جلب المنتجات من الذاكرة المؤقتة أو تحديثها إذا انتهى الوقت"""
    global _products_cache
    current_time = time.time()
    if _products_cache['data'] is None or (current_time - _products_cache['timestamp']) > CACHE_TTL:
        try:
            _products_cache['data'] = services.products.fetch_all_products_for_search()
            _products_cache['timestamp'] = current_time
        except Exception as e:
            print(f"❌ خطأ في جلب المنتجات للذاكرة المؤقتة: {e}")
            if _products_cache['data'] is None:
                return []
    return _products_cache['data']


def manage_products_view():
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
            return redirect(url_for('admin_dashboard_bp.dashboard'))
        
        # ✅ جلب معلمات الصفحة والبحث
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search_query = request.args.get('title', '', type=str)
        ajax = request.args.get('ajax', 0, type=int)
        
        # ✅ إذا كان هناك بحث، فلترة المنتجات فورياً من الذاكرة المؤقتة السريعة
        if search_query:
            all_products = get_cached_all_products()
            filtered = [p for p in all_products if search_query.lower() in p.get('title', '').lower()]
            total_products = len(filtered)
            total_pages = (total_products + per_page - 1) // per_page if total_products > 0 else 1
            
            if page > total_pages:
                page = total_pages
            
            start = (page - 1) * per_page
            end = start + per_page
            products = filtered[start:end]
            
            pagination_info = {
                'totalItems': total_products,
                'totalPages': total_pages,
                'currentPage': page,
                'hasNextPage': page < total_pages,
                'hasPrevPage': page > 1
            }
        else:
            result = services.products.get_products_page(page)
            products = result.get('data', [])
            pagination_info = result.get('pagination', {})
            total_products = pagination_info.get('totalItems', 0)
            total_pages = pagination_info.get('totalPages', 1)
        
        print(f"🔍 [DEBUG] Page: {page}, Total: {total_products}, Pages: {total_pages}")
        print(f"🔍 [DEBUG] Products in this page: {len(products)}")
        
        for product in products:
            mapping = ProductSupplierMapping.query.filter_by(product_qid=product.get('qid')).first()
            if mapping:
                supplier = Supplier.query.get(mapping.supplier_id)
                product['supplier_name'] = supplier.trade_name if supplier else 'غير معروف'
                product['supplier_id'] = mapping.supplier_id
            else:
                product['supplier_name'] = 'غير مرتبط'
                product['supplier_id'] = None
        
        pagination_data = {
            "currentPage": pagination_info.get('currentPage', page),
            "totalPages": pagination_info.get('totalPages', total_pages),
            "limit": len(products),
            "totalItems": pagination_info.get('totalItems', total_products),
            "perPage": per_page,
            "hasPrev": pagination_info.get('hasPrevPage', page > 1),
            "hasNext": pagination_info.get('hasNextPage', page < total_pages)
        }
        
        if ajax:
            return render_template(
                'admin/includes/_table_products.html',
                products=products,
                search_title=search_query,
                pagination=pagination_data
            )
        
        return render_template(
            'admin/admin_Product.html',
            products=products,
            search_title=search_query,
            pagination=pagination_data
        )
    except Exception as e:
        print(f"❌ خطأ في manage_products: {e}")
        flash(f'❌ حدث خطأ في تحميل المنتجات: {str(e)}', 'danger')
        
        if ajax:
            return '<div class="alert alert-danger">حدث خطأ في تحميل المنتجات</div>'
        
        return render_template(
            'admin/admin_Product.html',
            products=[],
            search_title=request.args.get('title', ''),
            pagination={
                "currentPage": 1, 
                "totalPages": 1, 
                "limit": 0, 
                "totalItems": 0,
                "hasPrev": False,
                "hasNext": False
            }
        )


def register_products_route(bp):
    bp.add_url_rule('/products', view_func=manage_products_view, methods=['GET'])
    return bp
