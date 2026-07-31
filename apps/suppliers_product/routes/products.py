# coding: utf-8
# 📂 apps/suppliers_product/routes/products.py (أو الملف المسؤول عن مسارات منتجات المورد)

from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping

@suppliers_product_bp.route('/products', methods=['GET'])
@login_required
def list_supplier_products():
    """عرض وإدارة منتجات المورد الحالي"""
    try:
        user_type = session.get('user_type')
        supplier_id = session.get('user_id') or session.get('supplier_id')

        if user_type != 'supplier' and user_type != 'admin':
            flash('❌ غيرحصرح لك بالدخول لهذه الصفحة', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))

        # جلب كل المنتجات من الخدمة
        result = services.products.get_all_products() or {}
        all_products = result.get('data', [])

        # تصفية المنتجات لتخص المورد الحالي فقط (إذا لم يكن مشرفاً)
        if user_type != 'admin' and supplier_id:
            supplier_mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
            supplier_qids = {m.product_qid for m in supplier_mappings}
            target_products = [p for p in all_products if p.get('qid') in supplier_qids]
        else:
            target_products = all_products

        # تغليف المنتجات بالشكل الذي يتوقعه القالب (item.product)
        formatted_products = [{'product': p} for p in target_products]

        return render_template(
            'suppliers/suppliers_product.html',
            products=formatted_products
        )

    except Exception as e:
        print(f"❌ خطأ في تحميل منتجات المورد: {e}")
        flash('❌ حدث خطأ في تحميل المنتجات', 'danger')
        return render_template('suppliers/suppliers_product.html', products=[])
