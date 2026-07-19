# coding: utf-8
# 📂 apps/admin_Product/routes_edit.py

from flask import render_template, flash, redirect, url_for, request
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient
from apps.models.supplier_db import Supplier
from apps.models.product_supplier_map import ProductSupplierMapping
from urllib.parse import unquote
import logging

logger = logging.getLogger(__name__)

@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    # فك الترميز للتأكد من وصول المعرف بشكل صحيح
    clean_qid = unquote(qid)
    
    try:
        # جلب الموردين النشطين
        suppliers = Supplier.query.filter_by(status='active').all()
        
        # جلب المجموعات باستخدام الاستعلام المعتمد
        col_response = QomrahGraphQLClient.execute_query("""query { findAllCollections { data { qid, title } } }""")
        all_collections = []
        if col_response and 'data' in col_response and col_response['data'].get('findAllCollections'):
            all_collections = col_response['data']['findAllCollections'].get('data', [])
        
        # جلب بيانات المورد المحلي
        mapping = ProductSupplierMapping.query.filter_by(product_qid=clean_qid).first()
        mapping_data = {"selected_supplier_id": mapping.supplier_id if mapping else None}

        # جلب بيانات المنتج من قمرة مع هيكل المتغيرات المحدث ليتوافق مع Schema قمرة الجديدة
        prod_query = """
        query GetProd($qid: String!) { 
            findProductByQid(qid: $qid) { 
                success 
                data { 
                    qid, title, description, slug, 
                    variants { 
                        quantity, 
                        pricing { price }, 
                        identification { sku }, 
                        displayTitle { ar } 
                    }, 
                    collections { qid } 
                } 
            } 
        }
        """
        response = QomrahGraphQLClient.execute_query(prod_query, {"qid": clean_qid})
        
        # التحقق من وجود بيانات المنتج
        if not response or 'data' not in response or not response['data'].get('findProductByQid'):
            raise Exception("تعذر الوصول لبيانات المنتج من خادم قمرة")
            
        product_data = response['data']['findProductByQid'].get('data', {})
        
        if not product_data:
            flash("المنتج غير موجود.")
            return redirect(url_for('admin_product_bp.manage_products'))

        # معالجة المتغيرات (Variants) لضمان استخراج الحقول الجديدة للواجهة
        variants = product_data.get('variants', [])
        if variants:
            for v in variants:
                # استخراج السعر
                pricing = v.get('pricing') or {}
                v['price'] = pricing.get('price', 0)
                
                # استخراج SKU من كائن identification
                identification = v.get('identification') or {}
                v['sku'] = identification.get('sku', '')
                
                # استخراج العنوان من كائن displayTitle
                display_title = v.get('displayTitle') or {}
                v['title'] = display_title.get('ar', 'متغير بدون عنوان')
        
        # معالجة المجموعات المختارة
        collections = product_data.get('collections', [])
        product_data['collection_ids'] = [c['qid'] for c in collections if c and 'qid' in c]

        return render_template(
            'admin/admin_edit_product.html', 
            product=product_data, 
            suppliers=suppliers, 
            all_collections=all_collections, 
            mapping=mapping_data
        )
                                
    except Exception as e:
        logger.error(f"خطأ في تحميل صفحة التعديل للـ qid {clean_qid}: {str(e)}")
        flash("حدث خطأ أثناء تحميل بيانات المنتج.")
        return redirect(url_for('admin_product_bp.manage_products'))
