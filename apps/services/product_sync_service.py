# coding: utf-8
# 📂 apps/services/product_sync_service.py

from apps.extensions import db
from apps.models.product_db import Product
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.services.graphql_client import QomrahGraphQLClient

def sync_products_from_qomra():
    """
    خدمة مزامنة المنتجات مع استعلام GraphQL المصحح طبقاً لمخطط السيرفر (ProductsResponse).
    """
    # استعلام مصحح يراعي الغلاف ProductsResponse والحقول الفرعية للعملة
    query = """
    query {
        findAllProducts {
            data {
                id
                title
                price
                currency {
                    code
                }
                quantity
                sku
                image_url
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
    
    # تفريغ قائمة المنتجات سواء كانت داخل data أو products أو مصفوفة مباشرة
    products_data = []
    if isinstance(products_response, dict):
        products_data = products_response.get('data') or products_response.get('products') or []
    elif isinstance(products_response, list):
        products_data = products_response

    if not products_data:
        return "تمت المزامنة بنجاح، لكن لم يتم العثور على منتجات لجلبها."

    synced_count = 0
    for item in products_data:
        qid = str(item.get('id') or item.get('qid') or '')
        if not qid:
            continue

        title = item.get('title') or item.get('name') or 'منتج بدون اسم'
        price = float(item.get('price') or 0)
        
        # استخراج كائن العملة بالشكل الصحيح
        currency_raw = item.get('currency')
        if isinstance(currency_raw, dict):
            currency = currency_raw.get('code') or currency_raw.get('symbol') or 'SAR'
        else:
            currency = currency_raw or 'SAR'

        quantity = int(item.get('quantity') or 0)
        sku = item.get('sku') or ''
        image_url = item.get('image_url') or item.get('image') or ''
        description = item.get('description') or ''

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
