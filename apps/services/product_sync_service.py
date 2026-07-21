# coding: utf-8
# 📂 apps/services/product_sync_service.py

from apps.extensions import db
from apps.models.product_db import Product
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.services.graphql_client import QomrahGraphQLClient

def sync_products_from_qomra():
    """
    خدمة مزامنة المنتجات مع توافق كامل لمخطط (ProductWithReviewIds).
    """
    # تم تحديث الاستعلام بناءً على الحقول الصحيحة المطلوبة من السيرفر
    query = """
    query {
        findAllProducts {
            data {
                qid
                title
                pricing {
                    price
                    currency {
                        code
                    }
                }
                quantity
                slug
                images
                description
            }
        }
    }
    """

    result = QomrahGraphQLClient.execute_query(query)
    
    if not result:
        raise Exception("فشل الاتصال بخادم قمرة أو تعذر جلب البيانات عبر GraphQL.")

    data = result.get('data', {})
    products_response = data.get('findAllProducts', {})
    
    # تفريغ قائمة المنتجات
    products_data = []
    if isinstance(products_response, dict):
        products_data = products_response.get('data') or products_response.get('products') or []
    elif isinstance(products_response, list):
        products_data = products_response

    if not products_data:
        return "تمت المزامنة بنجاح، لكن لم يتم العثور على منتجات لجلبها."

    synced_count = 0
    for item in products_data:
        qid = str(item.get('qid') or '')
        if not qid:
            continue

        title = item.get('title') or 'منتج بدون اسم'
        
        # 1. استخراج السعر والعملة من كائن pricing
        pricing_data = item.get('pricing') or {}
        if isinstance(pricing_data, dict):
            price = float(pricing_data.get('price') or pricing_data.get('amount') or 0)
            currency_raw = pricing_data.get('currency')
            if isinstance(currency_raw, dict):
                currency = currency_raw.get('code') or currency_raw.get('symbol') or 'SAR'
            else:
                currency = currency_raw or 'SAR'
        else:
            price = 0
            currency = 'SAR'

        quantity = int(item.get('quantity') or 0)
        sku = item.get('slug') or item.get('seo') or ''
        
        # 2. استخراج رابط الصورة من حقل images (سواء كان مصفوفة أو نصاً مباشرًا)
        images_raw = item.get('images')
        image_url = ''
        if isinstance(images_raw, list) and len(images_raw) > 0:
            if isinstance(images_raw[0], dict):
                image_url = images_raw[0].get('url') or images_raw[0].get('src') or ''
            else:
                image_url = str(images_raw[0])
        elif isinstance(images_raw, str):
            image_url = images_raw

        description = item.get('description') or ''

        # التحديث أو الإضافة في قاعدة البيانات
        product = Product.query.filter_by(qid=qid).first()
        if product:
            product.title = title
            product.price = price
            product.currency = currency
            product.quantity = quantity
            product.sku = sku
            product.image_url = image_url
            product.description = description
        else:
            product = Product(
                qid=qid, title=title, price=price, currency=currency,
                quantity=quantity, sku=sku, image_url=image_url, description=description
            )
            db.session.add(product)

            mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
            if not mapping:
                new_mapping = ProductSupplierMapping(product_qid=qid, supplier_id=1, status='active')
                db.session.add(new_mapping)

        synced_count += 1

    db.session.commit()
    return f"تمت مزامنة وتحديث {synced_count} منتجاً بنجاح من قمرة."
