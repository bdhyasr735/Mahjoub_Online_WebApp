# coding: utf-8
# 📂 apps/admin_Product/routes/products.py

from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier


def manage_products_view():
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
            return redirect(url_for('admin_dashboard_bp.dashboard'))
        
        # ✅ جلب معلمات الصفحة والبحث
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)  # 10 منتجات لكل صفحة
        search_query = request.args.get('title', '', type=str)
        ajax = request.args.get('ajax', 0, type=int)  # ✅ للتحقق من طلب AJAX
        
        # ✅ جلب جميع المنتجات من GraphQL
        all_products = services.products.get_all_products() or []
        
        # ✅ تطبيق البحث (استخدم title بدلاً من name)
        if search_query:
            all_products = [p for p in all_products if search_query.lower() in p.get('title', '').lower()]
        
        # ✅ حساب الترقيم
        total_products = len(all_products)
        total_pages = (total_products + per_page - 1) // per_page if total_products > 0 else 1
        
        # ✅ التأكد من أن الصفحة الحالية لا تتجاوز إجمالي الصفحات
        if page > total_pages:
            page = total_pages
        
        start = (page - 1) * per_page
        end = start + per_page
        products = all_products[start:end]
        
        # ✅ ربط الموردين بالمنتجات
        for product in products:
            mapping = ProductSupplierMapping.query.filter_by(product_qid=product.get('qid')).first()
            if mapping:
                supplier = Supplier.query.get(mapping.supplier_id)
                product['supplier_name'] = supplier.trade_name if supplier else 'غير معروف'
                product['supplier_id'] = mapping.supplier_id
            else:
                product['supplier_name'] = 'غير مرتبط'
                product['supplier_id'] = None
        
        # ✅ بناء بيانات الترقيم
        pagination_data = {
            "currentPage": page,
            "totalPages": total_pages,
            "limit": len(products),
            "totalItems": total_products,
            "perPage": per_page,
            "hasPrev": page > 1,
            "hasNext": page < total_pages
        }
        
        # ✅ إذا كان طلب AJAX، أعد الجدول فقط
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
