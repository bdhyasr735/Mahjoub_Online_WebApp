# coding: utf-8
# 📂 apps/suppliers_product/routes/products.py

from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping

@suppliers_product_bp.route('/products', methods=['GET'])
@login_required
def manage_supplier_products_view():
    """عرض وإدارة منتجات المورد الحالي (متوافق مع Registry)"""
    try:
        user_type = session.get('user_type')
        supplier_id = session.get('user_id') or session.get('supplier_id')

        if user_type != 'supplier' and user_type != 'admin':
            flash('❌ غير مصرح لك بالدخول لهذه الصفحة', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))

        # جلب المنتجات من الخدمة
        result = services.products.get_all_products() or {}
        all_products = result.get('data', [])

        # تصفية المنتجات للمورد الحالي
        if user_type != 'admin' and supplier_id:
            supplier_mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
            supplier_qids = {m.product_qid for m in supplier_mappings}
            target_products = [p for p in all_products if p.get('qid') in supplier_qids]
        else:
            target_products = all_products

        # تغليف المنتجات لتتطابق مع هيكل القالب (item.product)
        formatted_products = [{'product': p} for p in target_products]

        return render_template(
            'suppliers/suppliers_product.html',
            products=formatted_products
        )

    except Exception as e:
        print(f"❌ خطأ في manage_supplier_products_view: {e}")
        flash('❌ حدث خطأ في تحميل المنتجات', 'danger')
        return render_template('suppliers/suppliers_product.html', products=[])


def register_supplier_products_route(app):
    """دالة تسجيل مسارات وموديول منتجات الموردين المطلوبة من الـ Registry"""
    try:
        if 'suppliers_product_bp' not in app.blueprints:
            app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')
        print("✅ [Supplier Products Route]: تم تسجيل مسارات منتجات الموردين بنجاح.")
    except Exception as e:
        print(f"❌ [Supplier Products Route Error]: {e}")
