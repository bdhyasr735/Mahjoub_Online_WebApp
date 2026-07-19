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
    """مزامنة بيانات المنتج مع منصة قمرة وحفظ المورد محلياً"""
    data = request.json or {}
    qid = data.get('qid')
    supplier_id = data.get('supplier_id')
    
    if not qid:
        return jsonify({"status": "error", "message": "المعرف الفريد QID مفقود"}), 400

    # 1. صياغة الـ Mutation المحدثة
    # نستخدم نفس الهيكلية التي تطلبها المنصة في التحديث
    mutation = """
    mutation UpdateProduct($qid: String!, $input: UpdateProductInput!) {
        updateProduct(qid: $qid, input: $input) {
            success
            message
        }
    }
    """
    
    # تحضير المتغيرات - ملاحظة: نرسل نفس الهيكل الذي نجلبه في GET
    variables = {
        "qid": qid,
        "input": {
            "title": data.get('title'),
            "slug": data.get('slug'),
            "description": data.get('description'),
            "collectionIds": data.get('collection_ids', []),
            "variants": data.get('variants', []) # يتم إرسالها كما تم استقبالها من JS
        }
    }
    
    try:
        # إرسال التحديث إلى منصة قمرة
        qomrah_response = QomrahGraphQLClient.execute_query(mutation, variables)
        
        # التحقق من وجود أخطاء في الاستجابة
        if not qomrah_response or 'errors' in qomrah_response:
            error_msg = qomrah_response.get('errors', [{}])[0].get('message', 'خطأ في التحديث')
            logger.error(f"❌ خطأ من API قمرة: {error_msg}")
            return jsonify({"status": "error", "message": f"فشل التحديث في قمرة: {error_msg}"}), 500

        # 2. تحديث ربط المورد في قاعدة البيانات المحلية
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
                return jsonify({"status": "warning", "message": "تم تحديث المنتج في قمرة، لكن فشل حفظ المورد محلياً"})

        return jsonify({"status": "success", "message": "✅ تم الحفظ بنجاح!"})

    except Exception as e:
        logger.error(f"❌ خطأ برمي أثناء المزامنة: {str(e)}")
        return jsonify({"status": "error", "message": "حدث خطأ غير متوقع أثناء المعالجة"}), 500
