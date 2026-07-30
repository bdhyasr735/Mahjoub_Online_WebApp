# coding: utf-8
# 📂 apps/suppliers_product/routes/products.py

import traceback
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
        
        page = request.args.get('page', 1, type=int)
        per_page = 12
        search_query = request.args.get('title', '', type=str)
        
        if user_type != 'admin' and supplier_id:
            supplier_mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id).all()
            supplier_qids = [m.product_qid for m in supplier_mappings]
            
            all_products = services.products.fetch_all_products_for_search() if hasattr(services.products, 'fetch_all_products_for_search') else []
            filtered_by_supplier = [p for p in all_products if p.get('qid') in supplier_qids]
        else:
            filtered_by_supplier = services.products.fetch_all_products_for_search() if hasattr(services.products, 'fetch_all_products_for_search') else []

        # 🔍 طباعة تفاصيل أول منتج في الـ Terminal لفحص أسماء المفاتيح بدقة
        if filtered_by_supplier:
            print("🔍 [DEBUG API PRODUCT]:", filtered_by_supplier[0])

        if search_query:
            filtered = [p for p in filtered_by_supplier if search_query.lower() in p.get('title', '').lower() or search_query.lower() in str(p.get('sku', '')).lower()]
        else:
            filtered = filtered_by_supplier

        total_products = len(filtered_by_supplier)
        active_products = len([p for p in filtered_by_supplier if p.get('status', '').upper() == 'PUBLISHED'])
        draft_products = len([p for p in filtered_by_supplier if p.get('status', '').upper() == 'DRAFT'])

        total_items = len(filtered)
        total_pages = (total_items + per_page - 1) // per_page if total_items > 0 else 1
        if page > total_pages:
            page = total_pages
        
        start = (page - 1) * per_page
        end = start + per_page
        current_page_items = filtered[start:end]

        wrapped_items = []
        for prod in current_page_items:
            # استخراج السعر بجميع الاحتمالات الممكنة
            price = prod.get('price') or prod.get('sale_price') or prod.get('regular_price') or prod.get('cost') or 0
            prod['price'] = price
            
            # معالجة الصور بمرونة مطلقة
            images = prod.get('images') or prod.get('photos') or prod.get('image') or []
            processed_images = []
            if isinstance(images, list):
                for img in images:
                    if isinstance(img, dict) and (img.get('url') or img.get('src') or img.get('link')):
                        processed_images.append({'url': img.get('url') or img.get('src') or img.get('link')})
                    elif isinstance(img, str):
                        processed_images.append({'url': img})
            elif isinstance(images, str):
                processed_images.append({'url': images})
            
            prod['images'] = processed_images
            
            # توفير الهيكلين معا لضمان توافقهما مع أي قالب (item.product أو item مباشرة)
            wrapped_items.append({
                'product': prod,
                'title': prod.get('title'),
                'sku': prod.get('sku'),
                'price': price,
                'quantity': prod.get('quantity') or prod.get('stock') or 0,
                'status': prod.get('status'),
                'qid': prod.get('qid'),
                'images': processed_images
            })

        class PaginationMock:
            def __init__(self, items, page, per_page, total):
                self.items = items
                self.page = page
                self.per_page = per_page
                self.total = total
                self.pages = (total + per_page - 1) // per_page if total > 0 else 1
                self.has_prev = page > 1
                self.has_next = page < self.pages
                self.prev_num = page - 1 if self.has_prev else None
                self.next_num = page + 1 if self.has_next else None

            def iter_pages(self, left_edge=2, right_edge=2, left_current=2, right_current=2):
                last = 0
                for num in range(1, self.pages + 1):
                    if num <= left_edge or \
                       (num > self.page - left_current - 1 and num < self.page + right_current) or \
                       num > self.pages - right_edge:
                        if last + 1 != num:
                            yield None
                        yield num
                        last = num

        pagination_obj = PaginationMock(wrapped_items, page, per_page, total_items)

        def get_status_text(status):
            mapping_status = {
                'PUBLISHED': 'منشور',
                'DRAFT': 'مسودة',
                'REJECTED': 'مرفوض',
                'ARCHIVED': 'مؤرشف'
            }
            return mapping_status.get(str(status).upper(), status)

        def format_price(price):
            try:
                return f"{float(price):,.2f} ر.ي"
            except:
                return f"{price} ر.ي"

        return render_template(
            'suppliers/suppliers_product.html',
            products=pagination_obj,
            total_products=total_products,
            active_products=active_products,
            draft_products=draft_products,
            search_title=search_query,
            get_status_text=get_status_text,
            format_price=format_price
        )
        
    except Exception as e:
        print("❌ خطأ تفصيلي في manage_supplier_products_view:")
        traceback.print_exc()
        flash(f'❌ حدث خطأ في تحميل المنتجات: {str(e)}', 'danger')
        return render_template(
            'suppliers/suppliers_product.html',
            products=None,
            total_products=0,
            active_products=0,
            draft_products=0,
            search_title="",
            get_status_text=lambda s: s,
            format_price=lambda p: p
        )


def register_supplier_products_route(bp):
    bp.add_url_rule('/products', view_func=manage_supplier_products_view, methods=['GET'], endpoint='manage_supplier_products_view')
    return bp
