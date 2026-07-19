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
    """
    حفظ بيانات المنتج وتحديثها في قمرة وقاعدة البيانات المحلية
    """
    data = request.get_json()
    
    if not data or 'qid' not in data:
        return jsonify({"status": "error", "message": "معرف المنتج مفقود"}), 400

    try:
        # 1. تحديث قاعدة البيانات المحلية
        mapping = ProductSupplierMapping.query.filter_by(product_qid=data['qid']).first()
        supplier_id = data.get('supplier_id') if data.get('supplier_id') != "" else None
            
        if mapping:
            mapping.supplier_id = supplier_id
            mapping.internal_notes = data.get('internal_notes', '') 
        else:
            new_mapping = ProductSupplierMapping(
                product_qid=data['qid'], 
                supplier_id=supplier_id,
                internal_notes=data.get('internal_notes', '')
            )
            db.session.add(new_mapping)
        
        db.session.commit()

        # 2. بناء الـ Mutation المحدث ليشمل وصف المنتج
        mutation = """
        mutation UpdateProductInfo($id: String!, $input: UpdateProductInfoInput!) {
            updateProductInfo(id: $id, input: $input) {
                qid
                title
            }
        }
        """
        
        # 3. تجهيز المدخلات الشاملة (تم إضافة description)
        variables = {
            "id": str(data['qid']),
            "input": {
                "title": str(data.get('title', '')),
                "description": str(data.get('description', '')), # إضافة الوصف هنا
                "slug": str(data.get('slug', '')),
                "status": str(data.get('status', 'draft')),
                "quantity": int(data.get('quantity', 0)),
                "pricing": {
                    "price": float(data.get('price', 0)),
                    "compareAtPrice": float(data.get('compareAtPrice', 0)),
                    "originalPrice": float(data.get('originalPrice', 0))
                },
                "identification": {
                    "sku": str(data.get('sku', '')),
                    "barcode": str(data.get('barcode', ''))
                },
                "seo": {
                    "title": str(data.get('seo_title', '')),
                    "description": str(data.get('seo_description', ''))
                }
            }
        }
        
        # 4. تنفيذ التحديث
        response = QomrahGraphQLClient.execute_query(mutation, variables=variables)
        
        # 5. معالجة الأخطاء
        if response and 'errors' in response:
            error_details = response.get('errors')
            logger.error(f"❌ فشل تحديث قمرة لـ {data['qid']}: {error_details}")
            return jsonify({"status": "error", "message": "حدث خطأ أثناء التواصل مع خادم قمرة"}), 500
        
        return jsonify({"status": "success", "message": "تم حفظ كافة التعديلات بنجاح"}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ خطأ تقني للـ qid {data.get('qid')}: {str(e)}")
        return jsonify({"status": "error", "message": "حدث خطأ داخلي أثناء المعالجة"}), 500
