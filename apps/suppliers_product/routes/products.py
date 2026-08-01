# coding: utf-8
# 📂 apps/suppliers_product/routes/products.py

import traceback
from flask import render_template, request, redirect, url_for, flash, session, current_app, jsonify
from flask_login import login_required, current_user
from apps.suppliers_product.routes import suppliers_product_bp
from apps.services import services
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.extensions import db
from datetime import datetime


def get_status_text(status):
    status_map = {
        'PUBLISHED': 'منشور', 'DRAFT': 'مسودة', 'ARCHIVED': 'مؤرشف',
        'PENDING': 'قيد المراجعة', 'REJECTED': 'مرفوض',
        'OUT_OF_STOCK': 'نفد من المخزون', 'INACTIVE': 'غير نشط'
    }
    return status_map.get(status, status)


def format_price(price):
    if price is None: return '0.00 ر.س'
    try: return f"{float(price):,.2f} ر.س"
    except: return str(price)


# ✅ دالة مساعدة لتحديث بيانات المنتجات المرتبطة فقط (بدون جلب صفحات كثيرة)
def _sync_products_in_background(supplier_id):
    """
    تقوم بتحديث بيانات المنتجات المرتبطة بالمورد من الـ API
    لا تنشئ روابط جديدة، ولا تجلب صفحات عديدة، فقط تحديث البيانات الموجودة.
    """
    try:
        mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
        if not mappings:
            return
        
        updated_count = 0
        for mapping in mappings:
            qid = mapping.product_qid
            product_data = services.products.get_product_by_qid(qid)
            if product_data:
                mapping.updated_at = datetime.utcnow()
                updated_count += 1
            # إذا لم يوجد المنتج في الـ API، نتركه (لا نحذفه)
        
        db.session.commit()
        print(f"✅ [Sync Background] تم تحديث {updated_count} منتج للمورد {supplier_id}")
        
    except Exception as e:
        db.session.rollback()
        print(f"⚠️ [Sync Background Error] {e}")


@suppliers_product_bp.route('/products', methods=['GET'], endpoint='list_supplier_products')
@login_required
def manage_supplier_products_view():
    try:
        supplier_id = getattr(current_user, 'id', None) or session.get('supplier_id') or session.get('user_id')
        user_type = getattr(current_user, 'user_type', None) or session.get('user_type')
        is_admin = (user_type == 'admin' or getattr(current_user, 'is_admin', False))

        if user_type not in ('supplier', 'admin') and not is_admin:
            flash('❌ غير مصرح لك بالدخول', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))

        # ============================================================
        # 1. المزامنة الخلفية الذكية (مرة كل 10 دقائق)
        # ============================================================
        last_sync_key = f'_last_sync_{supplier_id}'
        if not is_admin and supplier_id:
            last_sync_time = session.get(last_sync_key)
            # ✅ إصلاح خطأ الوقت: تحويل last_sync_time إلى naive إذا كان aware
            if last_sync_time and hasattr(last_sync_time, 'tzinfo') and last_sync_time.tzinfo is not None:
                last_sync_time = last_sync_time.replace(tzinfo=None)
            if not last_sync_time or (datetime.utcnow() - last_sync_time).seconds > 600:  # 10 دقائق
                _sync_products_in_background(supplier_id)
                session[last_sync_key] = datetime.utcnow()

        # ============================================================
        # 2. جلب المنتجات المرتبطة فقط مع Pagination من قاعدة البيانات
        # ============================================================
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('limit', 10, type=int)
        per_page = max(1, min(per_page, 50))

        query = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id)
        # يمكن إضافة فلترة حسب الحالة إذا أردت:
        # query = query.filter_by(status='active')
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        mappings = pagination.items

        # ============================================================
        # 3. جلب تفاصيل المنتجات من الـ API (لكل منتج على حدة)
        # ============================================================
        products_data = []
        for mapping in mappings:
            qid = mapping.product_qid
            product = services.products.get_product_by_qid(qid)
            if product:
                products_data.append({
                    'mapping': mapping,
                    'product': product
                })
            else:
                # إذا لم يوجد في الـ API، نعرض البيانات المحلية فقط
                products_data.append({
                    'mapping': mapping,
                    'product': None
                })

        # ============================================================
        # 4. تجهيز بيانات الترقيم
        # ============================================================
        pagination_info = {
            'current_page': pagination.page,
            'total_pages': pagination.pages,
            'has_prev': pagination.has_prev,
            'has_next': pagination.has_next,
            'prev_num': pagination.prev_num,
            'next_num': pagination.next_num,
            'per_page': pagination.per_page,
            'total_items': pagination.total
        }

        return render_template(
            'suppliers/suppliers_product.html',
            products=products_data,
            pagination=pagination_info,
            get_status_text=get_status_text,
            format_price=format_price
        )

    except Exception as e:
        current_app.logger.error(f"خطأ غير متوقع: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع أثناء تحميل المنتجات', 'danger')
        return render_template(
            'suppliers/suppliers_product.html',
            products=[],
            pagination={'total_pages': 0, 'total_items': 0, 'current_page': 1},
            get_status_text=get_status_text,
            format_price=format_price
        )
