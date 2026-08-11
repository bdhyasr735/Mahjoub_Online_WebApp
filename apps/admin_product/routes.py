# -*- coding: utf-8 -*-
# 📂 apps/admin_product/routes.py
"""
متجر محجوب أونلاين (www.mahjoub.online) - Qumra Cloud Sandbox
محطة عبور واستعلامات مباشرة (Pass-through Proxy) دون حفظ المنتجات.
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
import json
import requests
from . import admin_product_bp
from .registry import MODULE_METADATA

# نقطة نهاية Qumra Cloud Sandbox API
QUMRA_GRAPHQL_URL = MODULE_METADATA.get("sandbox_graphql_endpoint", "https://api.qumra.cloud/sandbox/graphql")

# -----------------------------------------------------------------------------
# دالة مساعدة لتنفيذ استعلامات GraphQL (تمرير الطلبات)
# -----------------------------------------------------------------------------
def execute_graphql(payload):
    """
    يقوم بإرسال الطلب إلى Qumra Cloud GraphQL ويعيد النتيجة.
    إذا فشل الاتصال، يُعيد هيكل بيانات فارغ لتجنب انهيار الموقع.
    """
    try:
        response = requests.post(QUMRA_GRAPHQL_URL, json=payload, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"[Qumra API Error] Status: {response.status_code} - {response.text}")
            return {"data": {}}
    except Exception as e:
        print(f"[Qumra Connection Error] {e}")
        return {"data": {}}

# -----------------------------------------------------------------------------
# GET: عرض جدول المنتجات من Qumra Cloud مباشرة
# -----------------------------------------------------------------------------
@admin_product_bp.route('/', methods=['GET'])
@admin_product_bp.route('/list', methods=['GET'])
def list_products():
    """
    محطة عبور: استعلام عن المنتجات من Qumra Cloud وعرضها.
    """
    # 1. جلب المعاملات (Filters) من الـ URL
    search_query = request.args.get('q', '').strip().lower()
    status_filter = request.args.get('status', 'ALL')
    collection_filter = request.args.get('collection', 'ALL')
    supplier_filter = request.args.get('supplier', 'ALL').strip()
    
    # 2. صياغة استعلام GraphQL لجلب المنتجات (هذا مثال، عدّله حسب مخطط قمرة كلاود الحقيقي)
    # الفرضية أن الـ API يرجع قائمة products مع الحقول الأساسية
    query = """
    query GetProducts($filter: ProductFilterInput, $first: Int) {
        products(filter: $filter, first: $first) {
            edges {
                node {
                    id
                    qid
                    supplierId
                    supplierName
                    title
                    slug
                    status
                    description
                    price
                    compareAtPrice
                    costPrice
                    quantity
                    currency
                    images { fileUrl gallery }
                    collections
                    tags
                    variants { id name type price quantity }
                    createdAt
                    updatedAt
                }
            }
            pageInfo { hasNextPage endCursor }
            totalCount
        }
    }
    """
    # بناء متغيرات الفلترة (GraphQL Variables)
    variables = {"first": 50} # جلب 50 منتج كمثال
    
    # 3. تنفيذ الاستعلام
    result = execute_graphql({"query": query, "variables": variables})
    
    # 4. تحليل البيانات القادمة من GraphQL
    all_products = []
    try:
        raw_products = result.get("data", {}).get("products", {}).get("edges", [])
        for edge in raw_products:
            all_products.append(edge.get("node", {}))
    except Exception:
        all_products = []

    # 5. تطبيق الفلاتر (تتم هنا في الذاكرة المؤقتة لأنها "محطة عبور")
    filtered_products = []
    for p in all_products:
        matches_search = (
            search_query in p.get('title', '').lower() or
            search_query in p.get('slug', '').lower() or
            search_query in p.get('sku', '').lower() or
            search_query in p.get('supplier_name', '').lower()
        ) if search_query else True
        
        matches_status = (p.get('status') == status_filter) if status_filter != 'ALL' else True
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

    # 6. حساب الإحصائيات للمرة الواحدة
    total_products = len(filtered_products)
    active_products = sum(1 for p in filtered_products if p.get('status') == 'ACTIVE')
    admin_tracking_count = sum(1 for p in filtered_products if p.get('supplier_id') is None)
    supplier_tracking_count = sum(1 for p in filtered_products if p.get('supplier_id') is not None)
    total_variants = sum(len(p.get('variants', [])) for p in filtered_products)
    total_stock_qty = sum(p.get('quantity', 0) for p in filtered_products)
    
    all_collections = set()
    suppliers_map = {}
    for p in filtered_products:
        for c in p.get('collections', []):
            all_collections.add(c)
        sid = p.get('supplier_id')
        sname = p.get('supplier_name')
        if sid is not None and sname:
            suppliers_map[str(sid)] = sname

    return render_template(
        'admin_product/products_list.html',
        products=filtered_products,  # عرض القائمة المفلترة
        total_products=total_products,
        active_products=active_products,
        admin_tracking_count=admin_tracking_count,
        supplier_tracking_count=supplier_tracking_count,
        total_variants=total_variants,
        total_stock_qty=total_stock_qty,
        collections=list(all_collections),
        suppliers_map=suppliers_map,
        search_query=search_query,
        current_status=status_filter,
        current_collection=collection_filter,
        current_supplier=supplier_filter,
        brand_color=MODULE_METADATA.get("brand_color", "#4A154B"),
        store_url=MODULE_METADATA.get("store_url", "https://mahjoub.online"),
        sandbox_endpoint=QUMRA_GRAPHQL_URL
    )

# -----------------------------------------------------------------------------
# GET: نافذة رفع منتج جديد (محطة عبور)
# -----------------------------------------------------------------------------
@admin_product_bp.route('/new', methods=['GET'])
def new_product():
    return render_template(
        'admin_product/product_form.html',
        product=None,
        is_edit=False,
        brand_color=MODULE_METADATA.get("brand_color", "#4A154B"),
        store_url=MODULE_METADATA.get("store_url", "https://mahjoub.online")
    )

# -----------------------------------------------------------------------------
# GET: نافذة تعديل منتج موجود (محطة عبور تستعلم عن المنتج أولاً)
# -----------------------------------------------------------------------------
@admin_product_bp.route('/<product_id>/edit', methods=['GET'])
def edit_product(product_id):
    # استعلام لجلب بيانات هذا المنتج المفرد لملء النموذج
    query = """
    query GetProduct($id: ID!) {
        product(id: $id) {
            id qid supplierId supplierName title slug status description
            price compareAtPrice costPrice quantity currency
            images { fileUrl gallery }
            collections tags
            variants { id name type price quantity }
        }
    }
    """
    result = execute_graphql({"query": query, "variables": {"id": product_id}})
    product = result.get("data", {}).get("product")
    
    if not product:
        flash('عذراً، المنتج المطلوب غير موجود في قمرة كلاود.', 'error')
        return redirect(url_for('admin_product.list_products'))
        
    return render_template(
        'admin_product/product_form.html',
        product=product,
        is_edit=True,
        brand_color=MODULE_METADATA.get("brand_color", "#4A154B"),
        store_url=MODULE_METADATA.get("store_url", "https://mahjoub.online")
    )

# -----------------------------------------------------------------------------
# POST: محطة عبور لإنشاء منتج (إرسال Mutation إلى Qumra Cloud)
# -----------------------------------------------------------------------------
@admin_product_bp.route('/create', methods=['POST'])
def create_product():
    try:
        data = request.form if not request.is_json else request.get_json()
        
        # 1. تجهيز بيانات الـ Mutation بناءً على النموذج
        mutation = """
        mutation CreateProduct($input: ProductInput!) {
            productCreate(input: $input) {
                product { id title }
                userErrors { field message }
            }
        }
        """
        
        # 2. تكوين كائن الـ Input (عدل الأسماء حسب متطلبات Schema قمرة كلاود)
        product_input = {
            "title": data.get('title'),
            "slug": data.get('slug'),
            "status": data.get('status', 'ACTIVE'),
            "description": data.get('description'),
            "price": float(data.get('price', 0)),
            "compareAtPrice": float(data.get('compareAtPrice', 0)),
            "quantity": int(data.get('quantity', 0)),
            "collections": [c.strip() for c in data.get('collections', '').split(',') if c.strip()],
            "tags": [t.strip() for t in data.get('tags', '').split(',') if t.strip()],
            # يجب التأكد من تحويل الصور والمتغيرات إلى JSON وتنسيق يتوافق مع الـ API
            "images": {"fileUrl": "https://via.placeholder.com/600"}, 
            "variants": [] 
        }

        # 3. تنفيذ العملية
        result = execute_graphql({"query": mutation, "variables": {"input": product_input}})
        
        errors = result.get("data", {}).get("productCreate", {}).get("userErrors", [])
        if not errors:
            flash("تم إنشاء المنتج بنجاح عبر Qumra Cloud Sandbox!", "success")
            return redirect(url_for('admin_product.list_products'))
        else:
            flash(f"خطأ من قمرة كلاود: {errors[0].get('message')}", "error")
            
    except Exception as e:
        flash(f"حدث خطأ أثناء الحفظ: {str(e)}", "error")
        
    return redirect(url_for('admin_product.new_product'))

# -----------------------------------------------------------------------------
# POST: محطة عبور لتحديث منتج (إرسال Mutation إلى Qumra Cloud)
# -----------------------------------------------------------------------------
@admin_product_bp.route('/<product_id>/update', methods=['POST'])
def update_product(product_id):
    try:
        data = request.form if not request.is_json else request.get_json()

        mutation = """
        mutation UpdateProduct($id: ID!, $input: ProductInput!) {
            productUpdate(id: $id, input: $input) {
                product { id title }
                userErrors { field message }
            }
        }
        """
        product_input = {
            "title": data.get('title'),
            "slug": data.get('slug'),
            "status": data.get('status'),
            "description": data.get('description'),
            "price": float(data.get('price', 0)),
            "quantity": int(data.get('quantity', 0)),
        }

        result = execute_graphql({"query": mutation, "variables": {"id": product_id, "input": product_input}})
        
        errors = result.get("data", {}).get("productUpdate", {}).get("userErrors", [])
        if not errors:
            flash("تم تحديث المنتج في Qumra Cloud Sandbox بنجاح!", "success")
        else:
            flash(f"خطأ من قمرة كلاود: {errors[0].get('message')}", "error")

    except Exception as e:
        flash(f"حدث خطأ أثناء التحديث: {str(e)}", "error")

    return redirect(url_for('admin_product.list_products'))

# -----------------------------------------------------------------------------
# POST / DELETE: حذف منتج (إرسال Mutation إلى Qumra Cloud)
# -----------------------------------------------------------------------------
@admin_product_bp.route('/<product_id>/delete', methods=['POST', 'DELETE'])
def delete_product(product_id):
    try:
        mutation = """
        mutation DeleteProduct($id: ID!) {
            productDelete(id: $id) {
                deletedProductId
                userErrors { field message }
            }
        }
        """
        result = execute_graphql({"query": mutation, "variables": {"id": product_id}})
        
        errors = result.get("data", {}).get("productDelete", {}).get("userErrors", [])
        if not errors:
            flash("تم حذف المنتج من Qumra Cloud Sandbox بنجاح.", "success")
        else:
            flash(f"خطأ من قمرة كلاود: {errors[0].get('message')}", "error")
            
    except Exception as e:
        flash(f"حدث خطأ أثناء الحذف: {str(e)}", "error")
        
    return redirect(url_for('admin_product.list_products'))
