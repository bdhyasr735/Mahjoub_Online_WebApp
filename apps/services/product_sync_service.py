# coding: utf-8
# 📂 apps/services/product_sync_service.py

from apps.extensions import db
from apps.models.product_db import Product
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.services.graphql_client import QomrahGraphQLClient
import logging

def sync_products_from_qomra():
    """
    جلب المنتجات من منصة قمرة باستخدام QomrahGraphQLClient وحفظها في قاعدة البيانات المحلية بكل تفاصيلها،
    مع ربط المنتجات تلقائياً بجدول الموردين السيادي (ProductSupplierMapping).
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
    
    if not result or 'data' not in result or not result['data']:
        logging.error("❌ فشل في استرجاع البيانات من خدمة قمرة GraphQL.")
        raise Exception("فشل في استرجاع البيانات من خدمة قمرة GraphQL.")
        
    response_data = result['data'].get('findAllProducts', {})
    products_data = response_data.get('data', [])
    
    if not products_data:
        return "تمت المزامنة بنجاح، لكن لا توجد منتجات جديدة في المنصة."

    saved_count = 0
    updated_count = 0
    mappings_count = 0

    # محاولة العثور على المورد الافتراضي في النظام لربط المنتجات به مبدئياً
    default_supplier_id = 1
    try:
        from apps.models.supplier import Supplier
        first_supplier = Supplier.query.first()
        if first_supplier:
            default_supplier_id = first_supplier.id
    except Exception:
        pass

    for item in products_data:
        title = item.get('title')
        if not title:
            continue
            
        qid = item.get('qid')
        description = item.get('description', '')
        quantity = int(item.get('quantity', 0) or 0)
        
        images = item.get('images', [])
        image_url = images[0].get('fileUrl') if images and isinstance(images, list) else None
        
        pricing = item.get('pricing', {})
        price = float(pricing.get('price', 0) if pricing else 0)
        currency = 'ر.س'

        # 1. حفظ أو تحديث المنتج في جدول المنتجات المحلي
        product = None
        if qid:
            product = Product.query.filter_by(qid=qid).first()
        if not product:
            product = Product.query.filter_by(name=title).first()
            
        if product:
            product.qid = qid or product.qid
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
                qid=qid,
                name=title,
                price=price,
                currency=currency,
                quantity=quantity,
                image_url=image_url,
                description=description
            )
            db.session.add(new_product)
            saved_count += 1

        # 2. ضمان وجود سجل ربط سيادي في جدول ProductSupplierMapping لكل منتج يحمل qid
        if qid:
            mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
            if not mapping:
                new_mapping = ProductSupplierMapping(
                    product_qid=qid,
                    supplier_id=default_supplier_id,
                    status='active'
                )
                db.session.add(new_mapping)
                mappings_count += 1
                
    db.session.commit()
    return f"تمت المزامنة بنجاح! إضافة {saved_count}، تحديث {updated_count}، وربط {mappings_count} منتج."
