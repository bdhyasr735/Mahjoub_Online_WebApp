# coding: utf-8
# 📂 apps/suppliers_product/routes/products.py

import traceback
from flask import render_template, request, redirect, url_for, flash, session, current_app
from flask_login import login_required
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping

# ===== دوال مساعدة للقالب =====
def get_status_text(status):
    """تحويل حالة المنتج إلى نص عربي"""
    status_map = {
        'PUBLISHED': 'منشور',
        'DRAFT': 'مسودة',
        'ARCHIVED': 'مؤرشف',
        'PENDING': 'قيد المراجعة',
        'REJECTED': 'مرفوض',
        'OUT_OF_STOCK': 'نفد من المخزون',
        'INACTIVE': 'غير نشط'
    }
    return status_map.get(status, status)

def format_price(price):
    """تنسيق السعر مع رمز العملة"""
    if price is None:
        return '0.00 ر.س'
    try:
        return f"{float(price):,.2f} ر.س"
    except (ValueError, TypeError):
        return str(price)

# ===== المسارات =====
@suppliers_product_bp.route('/products', methods=['GET'])
@login_required
def manage_supplier_products_view():
    """عرض وإدارة منتجات المورد الحالي"""
    try:
        user_type = session.get('user_type')
        supplier_id = session.get('user_id') or session.get('supplier_id')

        if user_type not in ('supplier', 'admin'):
            flash('❌ غير مصرح لك بالدخول لهذه الصفحة', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))

        # ===== محاولة جلب المنتجات بأمان =====
        all_products = []
        try:
            result = services.products.get_all_products()
            if result and isinstance(result, dict):
                all_products = result.get('data', [])
            else:
                # إذا كانت النتيجة غير متوقعة، نعرض رسالة واضحة
                current_app.logger.warning(f"⚠️ نتيجة غير متوقعة من get_all_products: {result}")
                flash('⚠️ استجابة غير متوقعة من الخادم، تم عرض قائمة فارغة.', 'warning')
        except AttributeError as e:
            current_app.logger.error(f"❌ خدمة المنتجات غير مهيأة: {e}")
            flash('❌ خدمة المنتجات غير متوفرة حالياً. تأكد من تهيئة services.products.', 'danger')
        except Exception as e:
            current_app.logger.error(f"❌ خطأ في جلب المنتجات: {traceback.format_exc()}")
            flash(f'❌ حدث خطأ في جلب المنتجات: {str(e)}', 'danger')

        # ===== تصفية المنتجات للمورد الحالي =====
        target_products = []
        if all_products:
            try:
                if user_type != 'admin' and supplier_id:
                    supplier_mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
                    supplier_qids = {m.product_qid for m in supplier_mappings}
                    target_products = [p for p in all_products if p.get('qid') in supplier_qids]
                else:
                    target_products = all_products
            except Exception as e:
                current_app.logger.error(f"❌ خطأ في تصفية المنتجات: {traceback.format_exc()}")
                flash('❌ حدث خطأ في تصفية المنتجات', 'danger')

        # تغليف المنتجات للقالب
        formatted_products = [{'product': p} for p in target_products]

        return render_template(
            'suppliers/suppliers_product.html',
            products=formatted_products,
            get_status_text=get_status_text,
            format_price=format_price
        )

    except Exception as e:
        current_app.logger.error(f"❌ خطأ غير متوقع: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع في تحميل الصفحة', 'danger')
        # نعيد القالب مع قائمة فارغة على الأقل
        return render_template(
            'suppliers/suppliers_product.html',
            products=[],
            get_status_text=get_status_text,
            format_price=format_price
        )


def register_supplier_products_route(target_app):
    """تسجيل مسارات الموديول"""
    try:
        if hasattr(target_app, 'register_blueprint'):
            blueprint_name = getattr(suppliers_product_bp, 'name', 'suppliers_product_bp')
            if blueprint_name not in target_app.blueprints:
                target_app.register_blueprint(suppliers_product_bp, url_prefix='/supplier')
        print("✅ [Supplier Products Route]: تم تسجيل مسارات منتجات الموردين بنجاح.")
    except Exception as e:
        print(f"❌ [Supplier Products Route Error]: {e}")
