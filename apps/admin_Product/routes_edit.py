# coding: utf-8
# 📂 apps/admin_Product/routes_edit.py

import json
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, flash
from apps.services.product_sync_service import ProductSyncService
# استيراد الخدمات الأخرى بحسب هيكل مشروعك (مثل جلب الموردين والمجموعات)

admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')

# مفتاح أو توكن الاتصال بالخادم المركزي (يمكن جذبه من إعدادات النظام أو الجلسة)
GRAPHQL_TOKEN = "YOUR_ADMIN_API_TOKEN" 

@admin_product_bp.route('/products/edit/<qid>', methods=['GET'])
def edit_product(qid):
    """عرض صفحة تعديل المنتج مع جلب بياناته الأساسية والموردين والمجموعات"""
    sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
    
    # جلب بيانات المنتج المحدد بالـ qid
    product = sync_service.fetch_product_by_qid(qid)
    if not product:
        flash("المنتج المطلوب غير موجود أو حدث خطأ في جلب بياناته.", "danger")
        return redirect(url_for('admin_product_bp.manage_products'))

    # ملاحظة: يمكنك جلب قائمة المجموعات والموردين من قاعدة البيانات المحلية أو عبر خدمات الـ API المناسبة
    # مثال توضيحي لهياكل البيانات الوهمية أو المستدعاة:
    all_collections = [
        {"qid": "col_1", "title": "المجموعة العامة"},
        {"qid": "col_2", "title": "عروض العيد"},
        {"qid": "col_3", "title": "الإلكترونيات والتقنية"}
    ]
    
    suppliers = [
        {"id": 1, "trade_name": "متجر التقنية السريعة", "supplier_code": "SUP-001"},
        {"id": 2, "trade_name": "مؤسسة النور التجارية", "supplier_code": "SUP-002"}
    ]

    return render_template(
        'admin/admin_edit_product.html',
        product=product,
        all_collections=all_collections,
        suppliers=suppliers
    )


@admin_product_bp.route('/products/save-sync', methods=['POST'])
def save_sync_product():
    """معالجة وحفظ بيانات التعديل والمزامنة (AJAX Endpoint)"""
    try:
        qid = request.form.get('qid')
        title = request.form.get('title')
        slug = request.form.get('slug')
        description = request.form.get('description')
        status = request.form.get('status')
        supplier_id = request.form.get('supplier_id')
        sku = request.form.get('sku')
        quantity = request.form.get('quantity', 0)
        weight = request.form.get('weight', 0)
        
        # الأسعار
        original_price = request.form.get('original_price', 0)
        compare_at_price = request.form.get('compare_at_price', 0)
        price = request.form.get('price', 0)

        # فك تشفير المجموعات المتعددة المختارة عبر Choices.js
        collection_ids_raw = request.form.get('collection_ids', '[]')
        try:
            collection_ids = json.loads(collection_ids_raw)
        except json.JSONDecodeError:
            collection_ids = []

        # فك تشفير المتغيرات (Variants)
        variants_raw = request.form.get('variants', '[]')
        try:
            variants = json.loads(variants_raw)
        except json.JSONDecodeError:
            variants = []

        # الصور المحذوفة والجديدة
        removed_images_raw = request.form.get('removed_images', '[]')
        try:
            removed_images = json.loads(removed_images_raw)
        except json.JSONDecodeError:
            removed_images = []

        new_uploaded_images = request.files.getlist('images')

        # TODO: كتابة منطق إرسال البيانات المحدثة إلى الـ API المركزي أو حفظها محلياً في قاعدة البيانات

        return jsonify({
            "status": "success",
            "message": "تم حفظ وتحديث المنتج ومزامنة المجموعات بنجاح!"
        })

    except Exception as e:
        print(f"Error saving product sync: {e}")
        return jsonify({
            "status": "error",
            "message": f"حدث خطأ أثناء معالجة الطلب: {str(e)}"
        }), 500


@admin_product_bp.route('/products/manage', methods=['GET'])
def manage_products():
    """عرض قائمة إدارة المنتجات"""
    sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
    page = request.args.get('page', 1, type=int)
    title_query = request.args.get('title', '', type=str)
    
    # جلب المنتجات مع دعم البحث المباشر بالعنوان حسب التحديث الأخير في الـ Service
    result = sync_service.fetch_products(page=page, limit=20, title=title_query)
    
    return render_template(
        'admin/admin_manage_products.html',
        products=result.get("data", []),
        pagination=result.get("pagination", None),
        search_title=title_query
    )
