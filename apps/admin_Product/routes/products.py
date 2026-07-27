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
        per_page = request.args.get('per_page', 10, type=int)
        search_query = request.args.get('title', '', type=str)
        ajax = request.args.get('ajax', 0, type=int)
        
        # ✅ إذا كان هناك بحث، جلب جميع المنتجات للبحث
        if search_query:
            # ✅ استخدام الدالة الجديدة لجلب جميع المنتجات
            all_products = services.products.fetch_all_products_for_search()
            
            # ✅ تطبيق البحث
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
            # ✅ بدون بحث، جلب الصفحة المطلوبة فقط
            result = services.products.get_products_page(page)
            products = result.get('data', [])
            pagination_info = result.get('pagination', {})
            
            # ✅ التأكد من وجود بيانات
            total_products = pagination_info.get('totalItems', 0)
            total_pages = pagination_info.get('totalPages', 1)
        
        # ✅ طباعة للتحقق
        print(f"🔍 [DEBUG] Page: {page}, Total: {total_products}, Pages: {total_pages}")
        print(f"🔍 [DEBUG] Products in this page: {len(products)}")
        
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
            "currentPage": pagination_info.get('currentPage', page),
            "totalPages": pagination_info.get('totalPages', total_pages),
            "limit": len(products),
            "totalItems": pagination_info.get('totalItems', total_products),
            "perPage": per_page,
            "hasPrev": pagination_info.get('hasPrevPage', page > 1),
            "hasNext": pagination_info.get('hasNextPage', page < total_pages)
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


# ✅ دالة تعديل المنتج مع @login_required
@login_required
def edit_product_view(qid):
    """صفحة تعديل المنتج"""
    try:
        # ✅ تحقق من نوع المستخدم
        user_type = session.get('user_type')
        if user_type != 'admin':
            flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
            return redirect(url_for('admin_dashboard_bp.dashboard'))
        
        print(f"🔍 [edit_product] جلب المنتج بـ QID: {qid}")
        
        # ✅ جلب المنتج من الخدمة
        product = services.products.get_product_by_qid(qid)
        
        # ✅ إذا لم يتم العثور على المنتج
        if not product or not product.get('qid'):
            print(f"❌ [edit_product] المنتج غير موجود: {qid}")
            flash('❌ المنتج غير موجود', 'danger')
            return redirect(url_for('admin_product_bp.manage_products_view'))
        
        print(f"✅ [edit_product] تم جلب المنتج: {product.get('title')}")
        
        return render_template(
            'admin/admin_edit_product.html',
            product=product
        )
        
    except Exception as e:
        print(f"❌ [edit_product] خطأ: {e}")
        flash(f'❌ حدث خطأ: {str(e)}', 'danger')
        return redirect(url_for('admin_product_bp.manage_products_view'))


def register_products_route(bp):
    bp.add_url_rule('/products', view_func=manage_products_view, methods=['GET'])
    # ✅ أضف هذا السطر لتسجيل مسار التعديل
    bp.add_url_rule('/products/edit/<qid>', view_func=edit_product_view, methods=['GET'])
    return bp
