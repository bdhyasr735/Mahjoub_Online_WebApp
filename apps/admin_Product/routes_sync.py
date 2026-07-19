# coding: utf-8
# 📂 apps/admin_Product/routes_sync.py

from flask import request, jsonify
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
from apps.models import db
from apps.models.product_supplier_map import ProductSupplierMapping
import logging

logger = logging.getLogger(__name__)

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    data = request.get_json()
    
    if not data or 'qid' not in data:
        return jsonify({"status": "error", "message": "معرف المنتج مفقود"}), 400

    try:
        # 1. تحديث قاعدة البيانات المحلية
        mapping = ProductSupplierMapping.query.filter_by(product_qid=data['qid']).first()
        supplier_id = data.get('supplier_id') if str(data.get('supplier_id', '')).strip() != "" else None
            
        if mapping:
            mapping.supplier_id = supplier_id
        else:
            new_mapping = ProductSupplierMapping(product_qid=data['qid'], supplier_id=supplier_id)
            db.session.add(new_mapping)
        db.session.commit()

        # 2. بناء الـ Mutation (متوافق مع الهيكل الجديد)
        mutation = """
        mutation UpdateProductInfo($id: String!, $input: UpdateProductInfoInput!) {
            updateProductInfo(id: $id, input: $input) {
                qid
            }
        }
        """
        
        # 3. معالجة المتغيرات (Variants) لتطابق الهيكل الجديد للـ Mutation
        processed_variants = []
        for v in data.get('variants', []):
            processed_variants.append({
                "quantity": int(v.get('quantity', 0)),
                "pricing": {"price": float(v.get('price', 0))},
                "identification": {"sku": str(v.get('sku', ''))},
                "displayTitle": {"ar": str(v.get('title', ''))}
            })
        
        # 4. تجهيز متغيرات الطلب
        variables = {
            "id": str(data['qid']),
            "input": {
                "title": str(data.get('title', '')),
                "description": str(data.get('description', '')),
                "slug": str(data.get('slug', '')),
                "collection_ids": list(data.get('collection_ids', [])),
                "variants": processed_variants
            }
        }
        
        # 5. تنفيذ التحديث
        response = QomrahGraphQLClient.execute_query(mutation, variables=variables)
        
        if not response or 'errors' in response:
            error_details = response.get('errors') if response else "No response"
            logger.error(f"❌ فشل تحديث قمرة لـ {data['qid']}: {error_details}")
            return jsonify({"status": "error", "message": "خطأ في الاتصال بخادم قمرة (Validation Error)"}), 500
        
        return jsonify({"status": "success", "message": "تم الحفظ بنجاح"}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ تقني في save-sync للـ {data.get('qid')}: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
