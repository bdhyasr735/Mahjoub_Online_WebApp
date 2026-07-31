# coding: utf-8
# 📂 apps/suppliers_product/routes/products.py

import math
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


# ===== فئة مساعدة لمحاكاة Pagination (لتتوافق مع القالب) =====
class MockPagination:
    """محاكاة لكائن Pagination الخاص بـ Flask-SQLAlchemy ليعمل مع القوائم العادية"""
    def __init__(self, items, page, per_page, total):
        self.items = items          # العناصر في الصفحة الحالية
        self.page = page             # رقم الصفحة الحالية
        self.per_page = per_page     # عدد العناصر في الصفحة
        self.total = total           # إجمالي العناصر
        self.pages = math.ceil(total / per_page) if total > 0 else 0  # إجمالي الصفحات
        self.has_prev = page > 1
        self.has_next = page < self.pages
        self.prev_num = page - 1 if self.has_prev else None
        self.next_num = page + 1 if self.has_next else None

    def iter_pages(self, left_edge=2, left_current=2, right_current=2, right_edge=2):
        """توليد أرقام الصفحات للشريط السفلي (مشابهة لـ Flask-SQLAlchemy)"""
        if self.pages <= 1:
            return []
        
        pages = []
        last = 0
        for num in range(1, self.pages + 1):
            if (num <= left_edge) or \
               (num > self.page - left_current - 1 and num < self.page + right_current) or \
               (num > self.pages - right_edge):
                if last + 1 != num:
                    pages.append(None)  # تمثل النقاط (...)
                pages.append(num)
                last = num
        return pages


# ===== المسارات =====
@suppliers_product_bp.route('/products', methods=['GET'])
@login_required
def manage_supplier_products_view():
    """عرض وإدارة منتجات المورد الحالي مع البحث، الفلاتر، والترقيم (Ajax-ready)"""
    try:
        user_type = session.get('user_type')
        supplier_id = session.get('user_id') or session.get('supplier_id')

        if user_type not in ('supplier', 'admin'):
            flash('❌ غير مصرح لك بالدخول لهذه الصفحة', 'danger')
            return redirect(url_for('suppliers_dashboard_bp.dashboard'))

        # ===== 1. استلام معاملات البحث والفلاتر والترقيم =====
        page = request.args.get('page', 1, type=int)
        search_term = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        status = request.args.get('status', '').strip()
        min_price = request.args.get('min_price', '')
        max_price = request.args.get('max_price', '')
        is_ajax = request.args.get('ajax', '0') == '1'  # معرفة إذا كان طلب Ajax

        # ===== 2. جلب جميع المنتجات =====
        all_products = []
        try:
            result = services.products.get_all_products()
            if result and isinstance(result, dict):
                all_products = result.get('data', [])
            elif isinstance(result, list):
                all_products = result
            else:
                current_app.logger.warning(f"⚠️ نتيجة غير متوقعة من get_all_products: {type(result)}")
                flash('⚠️ استجابة غير متوقعة من الخادم، تم عرض قائمة فارغة.', 'warning')
        except AttributeError as e:
            current_app.logger.error(f"❌ خدمة المنتجات غير مهيأة: {e}")
            flash('❌ خدمة المنتجات غير متوفرة حالياً.', 'danger')
        except Exception as e:
            current_app.logger.error(f"❌ خطأ في جلب المنتجات: {traceback.format_exc()}")
            flash(f'❌ حدث خطأ في جلب المنتجات: {str(e)}', 'danger')

        # ===== 3. تصفية المنتجات للمورد الحالي =====
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

        # ===== 4. تطبيق البحث والفلاتر (في الذاكرة) =====
        filtered_products = []
        for p in target_products:
            # البحث (Title أو SKU)
            if search_term:
                title = str(p.get('title', '')).lower()
                sku = str(p.get('sku', '')).lower()
                if search_term.lower() not in title and search_term.lower() not in sku:
                    continue

            # فلتر الفئة
            if category and p.get('category') != category:
                continue

            # فلتر الحالة
            if status and p.get('status') != status:
                continue

            # فلتر السعر
            try:
                price_val = float(p.get('price') or p.get('sale_price') or p.get('regular_price') or 0)
                if min_price:
                    if price_val < float(min_price):
                        continue
                if max_price:
                    if price_val > float(max_price):
                        continue
            except (ValueError, TypeError):
                pass  # تجاهل المنتجات ذات السعر غير الصحيح عند التصفية

            filtered_products.append(p)

        # ===== 5. تطبيق الترقيم (Pagination) =====
        per_page = 10  # كما طلبت: 10 منتجات في كل صفحة
        total_items = len(filtered_products)
        
        # حساب نقاط البداية والنهاية
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        paged_products = filtered_products[start_idx:end_idx]

        # تحويل المنتجات إلى شكل القالب
        formatted_products = [{'product': p} for p in paged_products]

        # إنشاء كائن الترقيم
        pagination = MockPagination(
            items=formatted_products,
            page=page,
            per_page=per_page,
            total=total_items
        )

        # ===== 6. إرجاع الرد =====
        # إذا كان طلب Ajax، نعيد نفس القالب ليقوم الـ JavaScript باستخراج حاوية المنتجات
        if is_ajax:
            return render_template(
                'suppliers/suppliers_product.html',
                products=pagination,
                get_status_text=get_status_text,
                format_price=format_price
            )

        # إذا كان طلب عادي (تحميل الصفحة لأول مرة)
        return render_template(
            'suppliers/suppliers_product.html',
            products=pagination,
            get_status_text=get_status_text,
            format_price=format_price
        )

    except Exception as e:
        current_app.logger.error(f"❌ خطأ غير متوقع: {traceback.format_exc()}")
        flash('❌ حدث خطأ غير متوقع في تحميل الصفحة', 'danger')
        # عند حدوث خطأ، نعيد قائمة فارغة
        empty_pagination = MockPagination(items=[], page=1, per_page=10, total=0)
        return render_template(
            'suppliers/suppliers_product.html',
            products=empty_pagination,
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
