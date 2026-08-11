# -*- coding: utf-8 -*-
# 📂 apps/admin_product/routes.py
"""
متجر محجوب أونلاين (www.mahjoub.online) - Qumra Cloud Sandbox
Routes handling GET and POST requests for products & dynamic variants.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
import json
import uuid
from datetime import datetime
from . import admin_product_bp
from .registry import MODULE_METADATA, MODULE_NAME, MODULE_ICON, QUMRA_GRAPHQL_SCHEMAS

# قاعدة بيانات مؤقتة متصلة بالـ Sandbox لمتجر محجوب أونلاين
INITIAL_PRODUCTS = [
    {
        "id": "prod_101",
        "qid": "qid_prod_101",
        "supplier_id": 1,
        "supplier_name": "مورد العطور الباريسية والعود",
        "sku": "SKU-PERF-101",
        "title": "عطر الفخامة الملكي - محجوب أونلاين Signature",
        "slug": "royal-luxury-perfume-mahjoub",
        "status": "ACTIVE",
        "description": "عطر شرقي فاخر بتركيز عالي ونفحات من العود والصندل والمسك، مصمم خصيصاً لعملاء متجر محجوب أونلاين.",
        "price": 350.0,
        "compareAtPrice": 450.0,
        "costPrice": 210.0,
        "quantity": 85,
        "currency": "SAR",
        "weight_val": 0.5,
        "weight_unit": "kg",
        "dimensions": "10x10x15 cm",
        "images": {
            "fileUrl": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=600&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?w=600&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1547887537-6158d64c35b3?w=600&auto=format&fit=crop&q=80"
            ]
        },
        "collections": ["عطور فاخرة", "أحدث الصيحات", "الهدايا"],
        "tags": ["عطر", "عود", "محجوب_أونلاين", "قمرة_كلاود"],
        "variants": [
            {
                "id": "var_101_1",
                "name": "حجم 50 مل",
                "type": "Size",
                "price": 280.0,
                "quantity": 35
            },
            {
                "id": "var_101_2",
                "name": "حجم 100 مل",
                "type": "Size",
                "price": 350.0,
                "quantity": 50
            }
        ],
        "createdAt": "2026-08-01T10:00:00Z",
        "updatedAt": "2026-08-10T12:30:00Z"
    },
    {
        "id": "prod_102",
        "qid": "qid_prod_102",
        "supplier_id": None,
        "supplier_name": "تتبع الإدارة العامة",
        "sku": "SKU-[#4A154B]-WATCH-102",
        "title": "ساعة Qumra Smart Watch Pro",
        "slug": "qumra-smart-watch-pro",
        "status": "ACTIVE",
        "description": "ساعة ذكية متوافقة تماماً مع جميع الأجهزة بشاشة AMOLED وقياس المؤشرات الحيوية مع دعم كامل للغة العربية.",
        "price": 499.0,
        "compareAtPrice": 699.0,
        "costPrice": 320.0,
        "quantity": 120,
        "currency": "SAR",
        "weight_val": 0.2,
        "weight_unit": "kg",
        "dimensions": "8x8x5 cm",
        "images": {
            "fileUrl": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80",
            "gallery": [
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80",
                "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&auto=format&fit=crop&q=80"
            ]
        },
        "collections": ["إلكترونيات", "أجهزة ذكية"],
        "tags": ["ساعة", "ذكي", "محجوب_أونلاين", "QumraCloud"],
        "variants": [
            {
                "id": "var_102_1",
                "name": "أسود ملكي / 44mm",
                "type": "Color/Size",
                "price": 499.0,
                "quantity": 60
            },
            {
                "id": "var_102_2",
                "name": "فضي كلاسيك / 44mm",
                "type": "Color/Size",
                "price": 499.0,
                "quantity": 40
            },
            {
                "id": "var_102_3",
                "name": "ذهبي روز / 40mm",
                "type": "Color/Size",
                "price": 520.0,
                "quantity": 20
            }
        ],
        "createdAt": "2026-08-05T14:15:00Z",
        "updatedAt": "2026-08-09T16:00:00Z"
    },
    {
        "id": "prod_103",
        "qid": "qid_prod_103",
        "supplier_id": 3,
        "supplier_name": "مورد الجلديات والإكسسوارات الفاخرة",
        "sku": "SKU-LEATH-103",
        "title": "حقيبة جلد طبيعي فاخرة - طراز أكسفورد",
        "slug": "luxury-leather-bag-oxford",
        "status": "DRAFT",
        "description": "حقيبة مصنوعة يدوياً من الجلد الطبيعي 100% بتصميم أكسفورد الأنيق مع جيوب متعددة للكمبيوتر والأوراق.",
        "price": 290.0,
        "compareAtPrice": 380.0,
        "costPrice": 170.0,
        "quantity": 40,
        "currency": "SAR",
        "weight_val": 1.2,
        "weight_unit": "kg",
        "dimensions": "40x30x10 cm",
        "images": {
            "fileUrl": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=600&auto=format&fit=crop&q=80"
        },
        "collections": ["حقائب واكسسوارات", "منتجات جلدية"],
        "tags": ["جلد_طبيعي", "حقيبة", "أكسفورد"],
        "variants": [
            {
                "id": "var_103_1",
                "name": "بني كلاسيكي",
                "type": "Color",
                "price": 290.0,
                "quantity": 25
            },
            {
                "id": "var_103_2",
                "name": "أسود فاخر",
                "type": "Color",
                "price": 290.0,
                "quantity": 15
            }
        ],
        "createdAt": "2026-08-08T09:20:00Z",
        "updatedAt": "2026-08-08T09:20:00Z"
    }
]

# ذاكرة المخزن المؤقت في بيئة الـ Sandbox
PRODUCTS_DB = list(INITIAL_PRODUCTS)

def get_db_products():
    return PRODUCTS_DB

def find_product_by_id(prod_id):
    for p in PRODUCTS_DB:
        if str(p["id"]) == str(prod_id):
            return p
    return None

def generate_slug(text):
    if not text:
        return f"product-{uuid.uuid4().hex[:6]}"
    clean_slug = text.strip().lower().replace(" ", "-").replace("/", "-")
    return clean_slug

SUPPLIERS_MAP = {
    "1": "مورد العطور الباريسية والعود",
    "2": "مورد التكنولوجيا والأجهزة الذكية",
    "3": "مورد الجلديات والإكسسوارات الفاخرة",
    "4": "مورد الأزياء والموضة العالمية"
}

def parse_supplier_info(raw_supplier_id, raw_custom_name=None):
    if not raw_supplier_id or str(raw_supplier_id).strip() in ['', '0', 'none', 'null', 'admin', 'None']:
        return None, "تتبع الإدارة العامة"
    
    sup_id_str = str(raw_supplier_id).strip()
    if sup_id_str in SUPPLIERS_MAP:
        try:
            return int(sup_id_str), SUPPLIERS_MAP[sup_id_str]
        except ValueError:
            return sup_id_str, SUPPLIERS_MAP[sup_id_str]
    
    if raw_custom_name and str(raw_custom_name).strip():
        try:
            return int(sup_id_str), str(raw_custom_name).strip()
        except ValueError:
            return sup_id_str, str(raw_custom_name).strip()
            
    return sup_id_str, f"مورد (مُعرّف #{sup_id_str})"

# -----------------------------------------------------------------------------
# GET: عرض جدول المنتجات المستقلة (products_list.html)
# -----------------------------------------------------------------------------
@admin_product_bp.route('/', methods=['GET'])
@admin_product_bp.route('/list', methods=['GET'])
def list_products():
    """
    مسار عرض جدول المنتجات والمتغيرات مع خيارات التصفية والبحث
    """
    search_query = request.args.get('q', '').strip().lower()
    status_filter = request.args.get('status', 'ALL')
    collection_filter = request.args.get('collection', 'ALL')
    supplier_filter = request.args.get('supplier', 'ALL').strip()
    
    products = get_db_products()
    
    # تطبيق الفلترة
    filtered_products = []
    for p in products:
        matches_search = (
            search_query in p['title'].lower() or
            search_query in p['slug'].lower() or
            search_query in p['description'].lower() or
            search_query in (p.get('sku') or '').lower() or
            search_query in (p.get('qid') or '').lower() or
            search_query in (p.get('supplier_name') or '').lower() or
            any(search_query in t.lower() for t in p.get('tags', []))
        ) if search_query else True
        
        matches_status = (p['status'] == status_filter) if status_filter != 'ALL' else True
        matches_collection = (collection_filter in p.get('collections', [])) if collection_filter != 'ALL' else True
        
        matches_supplier = True
        if supplier_filter == 'ADMIN':
            matches_supplier = (p.get('supplier_id') is None)
        elif supplier_filter == 'SUPPLIERS':
            matches_supplier = (p.get('supplier_id') is not None)
        elif supplier_filter != 'ALL':
            matches_supplier = (str(p.get('supplier_id')) == supplier_filter)

        if matches_search and matches_status and matches_collection and matches_supplier:
            filtered_products.append(p)

    import math
    
    # معالجة التقليب (Pagination)
    try:
        current_page = max(1, int(request.args.get('page', 1)))
    except ValueError:
        current_page = 1
        
    try:
        per_page = max(1, int(request.args.get('per_page', 10)))
    except ValueError:
        per_page = 10
        
    total_filtered = len(filtered_products)
    total_pages = max(1, math.ceil(total_filtered / per_page))
    
    if current_page > total_pages:
        current_page = total_pages
        
    start_idx = (current_page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_products = filtered_products[start_idx:end_idx]

    # حساب إحصائيات المخزون
    total_products = len(products)
    active_products = sum(1 for p in products if p['status'] == 'ACTIVE')
    admin_tracking_count = sum(1 for p in products if p.get('supplier_id') is None)
    supplier_tracking_count = sum(1 for p in products if p.get('supplier_id') is not None)
    total_variants = sum(len(p.get('variants', [])) for p in products)
    total_stock_qty = sum(p['quantity'] for p in products)

    all_collections = set()
    for p in products:
        for c in p.get('collections', []):
            all_collections.add(c)

    return render_template(
        'admin_Product/products_list.html',
        products=paginated_products,
        total_filtered=total_filtered,
        current_page=current_page,
        per_page=per_page,
        total_pages=total_pages,
        total_products=total_products,
        active_products=active_products,
        admin_tracking_count=admin_tracking_count,
        supplier_tracking_count=supplier_tracking_count,
        total_variants=total_variants,
        total_stock_qty=total_stock_qty,
        collections=list(all_collections),
        search_query=search_query,
        current_status=status_filter,
        current_collection=collection_filter,
        current_supplier=supplier_filter,
        suppliers_map=SUPPLIERS_MAP,
        brand_color=MODULE_METADATA["brand_color"],
        store_url=MODULE_METADATA["store_url"],
        sandbox_endpoint=MODULE_METADATA["sandbox_graphql_endpoint"]
    )

# -----------------------------------------------------------------------------
# GET: نافذة رفع منتج جديد (product_form.html)
# -----------------------------------------------------------------------------
@admin_product_bp.route('/new', methods=['GET'])
def new_product():
    """
    واجهة إنشاء منتج جديد وتجهيز المتغيرات الديناميكية
    """
    return render_template(
        'admin_Product/product_form.html',
        product=None,
        is_edit=False,
        brand_color=MODULE_METADATA["brand_color"],
        store_url=MODULE_METADATA["store_url"],
        graphql_schema=QUMRA_GRAPHQL_SCHEMAS["MUTATION_CREATE_PRODUCT"]
    )

# -----------------------------------------------------------------------------
# GET: نافذة تعديل منتج قائم (product_form.html)
# -----------------------------------------------------------------------------
@admin_product_bp.route('/<product_id>/edit', methods=['GET'])
def edit_product(product_id):
    """
    واجهة تعديل البيانات والمتغيرات لمنتج موجود
    """
    product = find_product_by_id(product_id)
    if not product:
        flash('عذراً، المنتج المطلوب غير موجود أو تم حذفه.', 'error')
        return redirect(url_for('admin_product.list_products'))
        
    return render_template(
        'admin_Product/product_form.html',
        product=product,
        is_edit=True,
        brand_color=MODULE_METADATA["brand_color"],
        store_url=MODULE_METADATA["store_url"],
        graphql_schema=QUMRA_GRAPHQL_SCHEMAS["MUTATION_UPDATE_PRODUCT"]
    )

# -----------------------------------------------------------------------------
# POST: معالجة إنشاء منتج جديد مع المتغيرات الديناميكية والـ GraphQL
# -----------------------------------------------------------------------------
@admin_product_bp.route('/create', methods=['POST'])
def create_product():
    """
    دالة معالجة POST لإنشاء المنتج وتنسيق بياناته للربط مع قمرة كلاود
    """
    try:
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        title = data.get('title', '').strip()
        slug = data.get('slug', '').strip() or generate_slug(title)
        status = data.get('status', 'ACTIVE')
        description = data.get('description', '').strip()
        
        price = float(data.get('price', 0) or 0)
        compare_at_price = float(data.get('compareAtPrice', 0) or 0)
        cost_price = float(data.get('costPrice', 0) or data.get('cost_price', 0) or 0)
        quantity = int(data.get('quantity', 0) or 0)
        
        image_url = data.get('image_url', '').strip() or "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=600&auto=format&fit=crop&q=80"
        
        gallery = []
        raw_gallery_json = data.get('gallery_json', '[]')
        if raw_gallery_json and isinstance(raw_gallery_json, str):
            try:
                gallery = json.loads(raw_gallery_json)
            except Exception:
                gallery = [image_url]
        if not gallery:
            gallery = [image_url]
        
        raw_collections = data.get('collections', '')
        if isinstance(raw_collections, list):
            collections_list = raw_collections
        else:
            collections_list = [c.strip() for c in raw_collections.split(',') if c.strip()]
            
        raw_tags = data.get('tags', '')
        if isinstance(raw_tags, list):
            tags_list = raw_tags
        else:
            tags_list = [t.strip() for t in raw_tags.split(',') if t.strip()]

        raw_supplier_id = data.get('supplier_id')
        raw_supplier_name = data.get('supplier_name') or data.get('custom_supplier_name')
        sup_id, sup_name = parse_supplier_info(raw_supplier_id, raw_supplier_name)

        sku = data.get('sku', '').strip() or f"SKU-{uuid.uuid4().hex[:6].upper()}"
        qid = data.get('qid', '').strip() or f"qid_{uuid.uuid4().hex[:10]}"
        currency = data.get('currency', 'SAR').strip()
        weight_val = float(data.get('weight_val', 0) or 0)
        weight_unit = data.get('weight_unit', 'kg').strip()
        dimensions = data.get('dimensions', '').strip()

        variants = []
        raw_variants_json = data.get('variants_json', '[]')
        if raw_variants_json and isinstance(raw_variants_json, str):
            try:
                parsed_variants = json.loads(raw_variants_json)
                for var in parsed_variants:
                    variants.append({
                        "id": f"var_{uuid.uuid4().hex[:8]}",
                        "name": str(var.get('name', 'متغير فرعي')),
                        "type": str(var.get('type', 'Standard')),
                        "price": float(var.get('price', price) or price),
                        "quantity": int(var.get('quantity', 0) or 0)
                    })
            except Exception as e:
                print(f"[Variants Parser Warning] {e}")

        new_prod_id = f"prod_{uuid.uuid4().hex[:8]}"
        new_product_obj = {
            "id": new_prod_id,
            "qid": qid,
            "supplier_id": sup_id,
            "supplier_name": sup_name,
            "sku": sku,
            "title": title,
            "slug": slug,
            "status": status,
            "description": description,
            "price": price,
            "compareAtPrice": compare_at_price,
            "costPrice": cost_price,
            "quantity": quantity,
            "currency": currency,
            "weight_val": weight_val,
            "weight_unit": weight_unit,
            "dimensions": dimensions,
            "images": {
                "fileUrl": gallery[0] if gallery else image_url,
                "gallery": gallery
            },
            "collections": collections_list if collections_list else ["عام"],
            "tags": tags_list if tags_list else ["محجوب_أونلاين"],
            "variants": variants,
            "createdAt": datetime.utcnow().isoformat() + "Z",
            "updatedAt": datetime.utcnow().isoformat() + "Z"
        }

        PRODUCTS_DB.insert(0, new_product_obj)

        if request.is_json:
            return jsonify({
                "success": True,
                "message": f"تم إضافة المنتج '{title}' بنجاح وحفظه في Sandbox قمرة كلاود.",
                "product": new_product_obj,
                "redirect_url": url_for('admin_product.list_products')
            }), 201

        flash(f"تم إنشاء المنتج '{title}' والمتغيرات الديناميكية بنجاح وإرساله إلى Qumra Cloud Sandbox.", "success")
        return redirect(url_for('admin_product.list_products'))

    except Exception as e:
        print(f"[Create Product Error] {e}")
        if request.is_json:
            return jsonify({"success": False, "error": str(e)}), 400
        flash(f"حدث خطأ أثناء حفظ المنتج: {str(e)}", "error")
        return redirect(url_for('admin_product.new_product'))

# -----------------------------------------------------------------------------
# POST: معالجة تحديث منتج قائم والتعديل على المتغيرات
# -----------------------------------------------------------------------------
@admin_product_bp.route('/<product_id>/update', methods=['POST'])
def update_product(product_id):
    """
    دالة تحديث المنتج القائم في نظام Qumra Cloud Sandbox
    """
    product = find_product_by_id(product_id)
    if not product:
        if request.is_json:
            return jsonify({"success": False, "error": "المنتج غير موجود"}), 404
        flash("المنتج المطلوب غير موجود.", "error")
        return redirect(url_for('admin_product.list_products'))

    try:
        data = request.get_json() if request.is_json else request.form

        product['title'] = data.get('title', product['title']).strip()
        product['slug'] = data.get('slug', product['slug']).strip() or generate_slug(product['title'])
        product['status'] = data.get('status', product['status'])
        product['description'] = data.get('description', product['description']).strip()
        
        product['price'] = float(data.get('price', product['price']) or 0)
        product['compareAtPrice'] = float(data.get('compareAtPrice', product.get('compareAtPrice', 0)) or 0)
        if 'costPrice' in data or 'cost_price' in data:
            product['costPrice'] = float(data.get('costPrice', data.get('cost_price', product.get('costPrice', 0))) or 0)
        product['quantity'] = int(data.get('quantity', product['quantity']) or 0)
        
        raw_gallery_json = data.get('gallery_json')
        if raw_gallery_json and isinstance(raw_gallery_json, str):
            try:
                gallery = json.loads(raw_gallery_json)
                if gallery and len(gallery) > 0:
                    product['images'] = {
                        "fileUrl": gallery[0],
                        "gallery": gallery
                    }
            except Exception:
                pass

        raw_collections = data.get('collections')
        if raw_collections is not None:
            if isinstance(raw_collections, list):
                product['collections'] = raw_collections
            else:
                product['collections'] = [c.strip() for c in str(raw_collections).split(',') if c.strip()]

        raw_tags = data.get('tags')
        if raw_tags is not None:
            if isinstance(raw_tags, list):
                product['tags'] = raw_tags
            else:
                product['tags'] = [t.strip() for t in str(raw_tags).split(',') if t.strip()]

        raw_supplier_id = data.get('supplier_id')
        if raw_supplier_id is not None:
            raw_supplier_name = data.get('supplier_name') or data.get('custom_supplier_name')
            sup_id, sup_name = parse_supplier_info(raw_supplier_id, raw_supplier_name)
            product['supplier_id'] = sup_id
            product['supplier_name'] = sup_name

        if 'sku' in data and data.get('sku'):
            product['sku'] = data.get('sku').strip()
        if 'currency' in data and data.get('currency'):
            product['currency'] = data.get('currency').strip()
        if 'weight_val' in data and data.get('weight_val') != '':
            product['weight_val'] = float(data.get('weight_val', 0) or 0)
        if 'weight_unit' in data and data.get('weight_unit'):
            product['weight_unit'] = data.get('weight_unit').strip()
        if 'dimensions' in data:
            product['dimensions'] = data.get('dimensions', '').strip()

        raw_variants_json = data.get('variants_json')
        if raw_variants_json and isinstance(raw_variants_json, str):
            try:
                parsed_variants = json.loads(raw_variants_json)
                new_variants_list = []
                for var in parsed_variants:
                    var_id = var.get('id') or f"var_{uuid.uuid4().hex[:8]}"
                    new_variants_list.append({
                        "id": var_id,
                        "name": str(var.get('name', 'متغير')),
                        "type": str(var.get('type', 'Standard')),
                        "price": float(var.get('price', product['price']) or product['price']),
                        "quantity": int(var.get('quantity', 0) or 0)
                    })
                product['variants'] = new_variants_list
            except Exception as e:
                print(f"[Variants Update Error] {e}")

        product['updatedAt'] = datetime.utcnow().isoformat() + "Z"

        if request.is_json:
            return jsonify({
                "success": True,
                "message": f"تم تحديث المنتج '{product['title']}' بنجاح.",
                "product": product
            }), 200

        flash(f"تم تحديث المنتج '{product['title']}' بنجاح وتطبيق التعديلات في Qumra Cloud Sandbox.", "success")
        return redirect(url_for('admin_product.list_products'))

    except Exception as e:
        print(f"[Update Product Error] {e}")
        if request.is_json:
            return jsonify({"success": False, "error": str(e)}), 400
        flash(f"حدث خطأ أثناء تحديث المنتج: {str(e)}", "error")
        return redirect(url_for('admin_product.edit_product', product_id=product_id))

# -----------------------------------------------------------------------------
# POST / DELETE: حذف منتج من النظام
# -----------------------------------------------------------------------------
@admin_product_bp.route('/<product_id>/delete', methods=['POST', 'DELETE'])
def delete_product(product_id):
    """
    مسار حذف المنتج وإزالته من سجلات Sandbox قمرة كلاود
    """
    product = find_product_by_id(product_id)
    if not product:
        if request.is_json:
            return jsonify({"success": False, "error": "المنتج غير موجود"}), 404
        flash("المنتج المراد حذفه غير موجود.", "error")
        return redirect(url_for('admin_product.list_products'))

    title = product['title']
    PRODUCTS_DB[:] = [p for p in PRODUCTS_DB if str(p["id"]) != str(product_id)]

    if request.is_json:
        return jsonify({
            "success": True,
            "deletedProductId": product_id,
            "message": f"تم حذف المنتج '{title}' بنجاح من النظام."
        }), 200

    flash(f"تم حذف المنتج '{title}' بنجاح من متجر محجوب أونلاين.", "success")
    return redirect(url_for('admin_product.list_products'))

# -----------------------------------------------------------------------------
# API: استعراض المنتجات بصيغة JSON للربط مع GraphQL / الـ Frontend
# -----------------------------------------------------------------------------
@admin_product_bp.route('/api/json', methods=['GET'])
def api_get_products():
    """
    نقطة نهاية API لإرجاع جميع المنتجات والمتغيرات بصيغة JSON لاختبار استجابة قمرة كلاود
    """
    return jsonify({
        "store": MODULE_METADATA["store_url"],
        "sandbox_provider": MODULE_METADATA["backend_provider"],
        "total": len(PRODUCTS_DB),
        "products": PRODUCTS_DB
    }), 200
