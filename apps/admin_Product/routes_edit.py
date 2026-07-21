# coding: utf-8
# 📂 apps/admin_Product/routes_edit.py

import json
import os
from flask import Blueprint, render_template, request, jsonify, url_for, redirect, flash
from apps.services.product_sync_service import ProductSyncService

admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')

# مفتاح أو توكن الاتصال بالخادم المركزي (يُفضل جذبه من متغيرات البيئة)
GRAPHQL_TOKEN = os.environ.get('QUMRA_API_KEY', 'YOUR_ADMIN_API_TOKEN') 

@admin_product_bp.route('/products/edit/<qid>', methods=['GET'])
def edit_product(qid):
    """عرض صفحة تعديل المنتج مع جلب بياناته الأساسية والموردين والمجموعات"""
    sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
    
    # جلب بيانات المنتج المحدد بالـ qid باستخدام الاستعلام الشامل
    product = sync_service.fetch_product_by_qid(qid)
    if not product:
        flash("المنتج المطلوب غير موجود أو حدث خطأ في جلب بياناته.", "danger")
        return redirect(url_for('admin_product_bp.manage_products'))

    # جلب قائمة المجموعات والموردين (يمكن ربطها بقاعدتك المحلية أو خدمات الـ API)
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
    """معالجة وحفظ بيانات التعديل والمزامنة (AJAX Endpoint) عبر الـ Mutation"""
    try:
        qid = request.form.get('qid')
        if not qid:
            return jsonify({"status": "error", "message": "معرف المنتج (qid) مفقود."}), 400

        title = request.form.get('title', '')
        slug = request.form.get('slug', '')
        description = request.form.get('description', '')
        status = request.form.get('status', 'DRAFT')
        sku = request.form.get('sku', '')
        
        # الأسعار
        try:
            price = float(request.form.get('price', 0))
            compare_at_price = float(request.form.get('compare_at_price', 0))
            cost_price = float(request.form.get('original_price', 0))
        except ValueError:
            price, compare_at_price, cost_price = 0.0, 0.0, 0.0

        # الأبعاد والوزن
        try:
            weight_val = float(request.form.get('weight', 0))
        except ValueError:
            weight_val = 0.0

        # تجهيز الهياكل المطلوبة للـ Mutation بدقة
        info = {
            "title": title,
            "slug": slug,
            "status": status
        }
        
        pricing = {
            "price": price,
            "compareAtPrice": compare_at_price,
            "costPrice": cost_price,
            "currency": "YER" # أو العملة المعتمدة لديك
        }
        
        dims = {
            "length": 0,
            "width": 0,
            "height": 0,
            "unit": "cm"
        }
        
        weight = {
            "value": weight_val,
            "unit": "kg"
        }
        
        ident = {
            "sku": sku
        }

        # فك تشفير المجموعات والمتغيرات المختارة
        collection_ids = json.loads(request.form.get('collection_ids', '[]') or '[]')
        variants = json.loads(request.form.get('variants', '[]') or '[]')

        # استدعاء خدمة المزامنة لتنفيذ الـ Mutation المعتمد
        sync_service = ProductSyncService(token=GRAPHQL_TOKEN)
        success = sync_service.update_product_data(
            qid=qid,
            info=info,
            pricing=pricing,
            dims=dims,
            weight=weight,
            ident=ident,
            desc=description
        )

        if not success:
            return jsonify({
                "status": "error",
                "message": "فشل حفظ التعديلات على الخادم المركزي."
            }), 500

        return jsonify({
            "status": "success",
            "message": "تم حفظ وتحديث المنتج ومزامنة بياناته بنجاح!"
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
    
    # جلب المنتجات مع دعم البحث المباشر بالعنوان
    result = sync_service.fetch_products(page=page, limit=20, title=title_query)
    
    return render_template(
        'admin/admin_manage_products.html',
        products=result.get("data", []),
        pagination=result.get("pagination", None),
        search_title=title_query
    )
