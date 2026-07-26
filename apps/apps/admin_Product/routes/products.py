# coding: utf-8
# 📂 apps/admin_Product/routes/products.py
# عرض قائمة المنتجات

from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_required
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier_db import Supplier


def manage_products_view():
    """عرض قائمة المنتجات مع دعم الترقيم والبحث"""
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
            return redirect(url_for('admin_dashboard_bp.dashboard'))
        
        search_query = request.args.get('title', '', type=str)
        page = request.args.get('page', 1, type=int)
        
        # جلب جميع المنتجات من السيرفر عبر الخدمة المركزية
        products = services.products.get_all_products()
        
        if search_query:
            products = [p for p in products if search_query.lower() in p.get('name', '').lower()]
        
        # ربط الموردين إن وجدوا
        for product in products:
            mapping = ProductSupplierMapping.query.filter_by(
                product_qid=product.get('qid')
            ).first()
            if mapping:
                supplier = Supplier.query.get(mapping.supplier_id)
                product['supplier_name'] = supplier.trade_name if supplier else 'غير معروف'
                product['supplier_id'] = mapping.supplier_id
            else:
                product['supplier_name'] = 'غير مرتبط'
                product['supplier_id'] = None
        
        return render_template(
            'admin/admin_Product.html',
            products=products,
            search_title=search_query,
            pagination={"currentPage": page, "totalPages": 1, "limit": len(products)}
        )
    except Exception as e:
        print(f"❌ خطأ في manage_products: {e}")
        flash(f'❌ حدث خطأ في تحميل المنتجات: {str(e)}', 'danger')
        return render_template(
            'admin/admin_Product.html',
            products=[],
            search_title=request.args.get('title', ''),
            pagination={"currentPage": 1, "totalPages": 1, "limit": 0}
        )


# ✅ تسجيل الـ Route يدوياً بعد إنشاء الـ Blueprint
def register_products_route(bp):
    """تسجيل Route المنتجات على Blueprint معين"""
    bp.add_url_rule('/products', view_func=manage_products_view, methods=['GET'])
    return bp
