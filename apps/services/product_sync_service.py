# coding: utf-8
# 📂 apps/services/product_sync_service.py

import uuid
import logging
from apps.extensions import db
from apps.models.product_db import Product
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.services.graphql_client import QomrahGraphQLClient

def sync_products_from_qomra():
    """
    جلب المنتجات من منصة قمرة باستخدام QomrahGraphQLClient وحفظها في قاعدة البيانات المحلية بكل تفاصيلها،
    مع دعم مرن لهيكل الاستجابة وربط المنتجات تلقائياً بجدول الموردين السيادي.
    """
    query = """
    query GetProductsList {
      findAllProducts {
        data {
          qid
          title
          description
          quantity
          images {
            _id
            fileUrl
          }
          pricing {
            price
          }
        }
        success
        message
      }
    }
    """
    
    # تنفيذ الاستعلام عبر الكلاس المعتمد
    result = QomrahGraphQLClient.execute_query(query)
    
    # طباعة الاستجابة الخام في السجلات لفحصها بدقة
    logging.info(f"🔍 [Qomra Sync Raw Response]: {result}")
    
    if not result:
        logging.error("❌ لم يتم استلام أي استجابة من خدمة قمرة GraphQL.")
        raise Exception("فشل في استرجاع البيانات من خدمة قمرة GraphQL (استجابة فارغة).")
        
    # استخراج البيانات بمرونة تامة لجميع الاحتمالات الهيكلية للاستجابة
    response_data = result.get('data', result)
    products_data = []

    if isinstance(response_data, dict):
        # البحث داخل حقل findAllProducts أو أي مفتاح رئيسي بديل
        find_all = response_data.get('findAllProducts') or response_data.get('data') or response_data
        if isinstance(find_all, dict):
            products_data = find_all.get('data') or find_all.get('items') or []
        elif isinstance(find_all, list):
            products_data = find_all
    elif isinstance(response_data, list):
        products_data = response_data

    logging.info(f"📦 [Parsed Products Count]: {len(products_data)}")

    if not products_data:
        return "تمت المزامنة بنجاح، لكن هيكل الاستجابة لم يعيد أي منتجات. راجع سجلات السيرفر (Logs) للتفاصيل."

    saved_count = 0
    updated_count = 0
    mappings_count = 0

    # جلب المورد الافتراضي في النظام لربط المنتجات به مبدئياً
    default_supplier_id = 1
    try:
        from apps.models.supplier_db import Supplier
        first_supplier = Supplier.query.first()
        if first_supplier:
            default_supplier_id = first_supplier.id
    except Exception:
        pass

    for item in products_data:
        if not isinstance(item, dict):
            continue
            
        # دعم أسماء حقول متعددة تحسساً لاختلاف واجهة قمرة
        title = item.get('title') or item.get('name')
        if not title:
            continue
            
        qid = item.get('qid') or item.get('_id') or item.get('id')
        description = item.get('description', '')
        
        try:
            quantity = int(item.get('quantity', 0) or 0)
        except (ValueError, TypeError):
            quantity = 0
        
        # استخراج الصورة بمرونة
        images = item.get('images', [])
        image_url = None
        if images and isinstance(images, list):
            first_img = images[0]
            if isinstance(first_img, dict):
                image_url = first_img.get('fileUrl') or first_img.get('url') or first_img.get('path')
            elif isinstance(first_img, str):
                image_url = first_img
        
        # استخراج السعر بمرونة
        pricing = item.get('pricing', {})
        price_val = 0
        if isinstance(pricing, dict):
            price_val = pricing.get('price', 0)
        elif isinstance(pricing, (int, float, str)):
            price_val = pricing
            
        try:
            price = float(price_val or 0)
        except (ValueError, TypeError):
            price = 0.0

        currency = 'ر.س'
        product_qid_str = str(qid) if qid else f"qomra_{uuid.uuid4().hex[:8]}"

        # 1. حفظ أو تحديث المنتج في جدول المنتجات المحلي
        product = None
        if qid:
            product = Product.query.filter_by(qid=str(qid)).first()
        if not product:
            product = Product.query.filter_by(name=title).first()
            
        if product:
            product.qid = product_qid_str
            product.name = title
            product.price = price
            product.currency = currency
            product.quantity = quantity
            if image_url:
                product.image_url = image_url
            product.description = description
            updated_count += 1
        else:
            new_product = Product(
                qid=product_qid_str,
                name=title,
                price=price,
                currency=currency,
                quantity=quantity,
                image_url=image_url,
                description=description
            )
            db.session.add(new_product)
            saved_count += 1

        # 2. ضمان وجود سجل ربط سيادي في جدول ProductSupplierMapping
        if product_qid_str:
            mapping = ProductSupplierMapping.query.filter_by(product_qid=product_qid_str).first()
            if not mapping:
                new_mapping = ProductSupplierMapping(
                    product_qid=product_qid_str,
                    supplier_id=default_supplier_id,
                    status='active'
                )
                db.session.add(new_mapping)
                mappings_count += 1
                
    db.session.commit()
    return f"تمت المزامنة بنجاح! إضافة {saved_count}، تحديث {updated_count}، وربط {mappings_count} منتج."
