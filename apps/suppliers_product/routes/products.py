# coding: utf-8
# 📂 apps/suppliers_product/routes/products.py

from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier


def manage_supplier_products_view():
    try:
        user_type = session.get('user_type')
        supplier_id = session.get('user_id') or session.get('supplier_id')

        if user_type != 'supplier' and user_type != 'admin':
            flash('❌ هذا القسم مخصص للموردين فقط', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))
        
        # ✅ جلب معلمات الصفحة والبحث
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search_query = request.args.get('title', '', type=str)
        ajax = request.args.get('ajax', 0, type=int)
        
        # إذا لم يكن المستخدم مشرفاً، نقوم بجلب المنتجات الخاصة بالمورد الحالي فقط عبر جدول الربط
        if user_type != 'admin' and supplier_id:
            supplier_mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
            supplier_qids = [m.product_qid for m in supplier_mappings]
            
            # جلب المنتجات من الـ API وتصفيتها لتقتصر على منتجات المورد
            all_products = services.products.fetch_all_products_for_search() if hasattr(services.products, 'fetch_all_products_for_search') else []
            filtered_by_supplier = [p for p in all_products if p.get('qid') in supplier_qids]
            
            if search_query:
                filtered = [p for p in filtered_by_supplier if search_query.lower() in p.get('title', '').lower()]
            else:
                filtered = filtered_by_supplier
            
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
            # إذا كان المشرف (admin) هو من يتصفح صفحة الموردين، يمكنه رؤية الكل أو التحكم بحسب الحاجة
            if search_query:
                all_products = services.products.fetch_all_products_for_search()
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
        
        print(f"🔍 [DEBUG Supplier Products] Page: {page}, Total: {total_products}, Pages: {total_pages}")
        print(f"🔍 [DEBUG Supplier Products] Products in this page: {len(products)}")
        
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
                'suppliers/includes/_table_supplier_products.html',
                products=products,
                search_title=search_query,
                pagination=pagination_data
            )
        
        return render_template(
            'suppliers/supplier_products.html',
            products=products,
            search_title=search_query,
            pagination=pagination_data
        )
        
    except Exception as e:
        print(f"❌ خطأ في manage_supplier_products_view: {e}")
        flash(f'❌ حدث خطأ في تحميل المنتجات: {str(e)}', 'danger')
        
        if ajax:
            return '<div class="alert alert-danger">حدث خطأ في تحميل المنتجات</div>'
        
        return render_template(
            'suppliers/supplier_products.html',
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


def register_supplier_products_route(bp):
    bp.add_url_rule('/products', view_func=manage_supplier_products_view, methods=['GET'])
    return bp
