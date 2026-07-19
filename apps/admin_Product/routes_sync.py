# coding: utf-8
# 📂 apps/admin_Product/routes_sync.py

from flask import request, jsonify
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
import logging

try:
    from apps.models.product_supplier_map import ProductSupplierMapping
    from apps.extensions import db
    HAS_DB = True
except ImportError:
    HAS_DB = False

logger = logging.getLogger(__name__)

@admin_product_bp.route('/save-sync', methods=['POST'])
def save_sync():
    """مزامنة بيانات المنتج مع منصة قمرة وحفظ المورد محلياً باستخدام الـ Handle"""
    data = request.json or {}
    qid = data.get('qid')
    supplier_id = data.get('supplier_id')
    
    if not qid:
        return jsonify({"status": "error", "message": "المعرف الفريد QID مفقود"}), 400

    # 1. معالجة البيانات بأمان
    try:
        raw_variants = data.get('variants', [])
        processed_variants = []
        for v in raw_variants:
            processed_variants.append({
                "title": str(v.get('title', '')),
                "price": float(v.get('price') or 0),
                "quantity": int(v.get('quantity') or 0),
                "sku": str(v.get('sku', ''))
            })

        price_data = {
            "price": float(data.get('price') or 0),
            "compareAtPrice": float(data.get('compare_at_price') or 0),
            "originalPrice": float(data.get('original_price') or 0)
        }
    except (ValueError, TypeError) as e:
        return jsonify({"status": "error", "message": f"خطأ في تنسيق البيانات الرقمية: {str(e)}"}), 400

    # 2. صياغة الـ Mutation
    mutation = """
    mutation UpdateProduct($qid: String!, $input: UpdateProductInput!) {
        updateProduct(qid: $qid, input: $input) {
            success
            message
        }
    }
    """
    
    # 3. بناء المتغيرات (تم استبدال collectionIds بـ collectionHandles)
    variables = {
        "qid": qid,
        "input": {
            "title": data.get('title'),
            "slug": data.get('slug'),
            "description": data.get('description'),
            "status": data.get('status'),
            "collectionHandles": data.get('collection_handles', []),
            "variants": processed_variants,
            "pricing": price_data,
            "images": data.get('images', []) 
        }
    }
    
    try:
        # إرسال التحديث إلى منصة قمرة
        qomrah_response = QomrahGraphQLClient.execute_query(mutation, variables)
        
        if not qomrah_response or 'errors' in qomrah_response:
            error_msg = qomrah_response.get('errors', [{}])[0].get('message', 'خطأ غير معروف في التحديث')
            logger.error(f"❌ خطأ من API قمرة: {error_msg}")
            return jsonify({"status": "error", "message": f"فشل التحديث في قمرة: {error_msg}"}), 500

        # 4. تحديث ربط المورد في قاعدة البيانات المحلية
        if HAS_DB:
            try:
                mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
                if supplier_id: 
                    if mapping:
                        mapping.supplier_id = supplier_id
                    else:
                        new_mapping = ProductSupplierMapping(product_qid=qid, supplier_id=supplier_id)
                        db.session.add(new_mapping)
                else: 
                    if mapping:
                        db.session.delete(mapping)
                
                db.session.commit()
            except Exception as db_err:
                db.session.rollback()
                logger.error(f"⚠️ فشل حفظ المورد محلياً: {str(db_err)}")
                return jsonify({"status": "warning", "message": "تم تحديث المنتج في قمرة، لكن حدث خطأ أثناء حفظ المورد محلياً"})

        return jsonify({"status": "success", "message": "✅ تم الحفظ بنجاح!"})

    except Exception as e:
        logger.error(f"❌ خطأ برمي أثناء المزامنة: {str(e)}")
        return jsonify({"status": "error", "message": "حدث خطأ غير متوقع أثناء المعالجة"}), 500
