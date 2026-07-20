# coding: utf-8
# 📂 apps/services/product_sync_service.py

from apps.extensions import db
from apps.models.product_db import Product
from apps.services.graphql_client import QomrahGraphQLClient

def sync_products_from_qomra():
    """
    جلب المنتجات من منصة قمرة باستخدام QomrahGraphQLClient وحفظها في قاعدة البيانات المحلية.
    """
    # استعلام GraphQL لجلب قائمة المنتجات
    query = """
    query GetProductsList {
      products {
        data {
          qid
          title
          description
          pricing {
            price
          }
        }
      }
    }
    """
    
    # تنفيذ الاستعلام عبر الكلاس المعتمد
    result = QomrahGraphQLClient.execute_query(query)
    
    if not result or 'data' not in result or not result['data']:
        raise Exception("فشل في استرجاع البيانات من خدمة قمرة GraphQL.")
            
    products_data = result['data'].get('products', {}).get('data', [])
    
    if not products_data:
        return "تمت المزامنة بنجاح، لكن لا توجد منتجات جديدة في المنصة."

    saved_count = 0
    for item in products_data:
        title = item.get('title')
        if not title:
            continue
                
        description = item.get('description', '')
        pricing = item.get('pricing', {})
        price = float(pricing.get('price', 0) if pricing else 0)

        # التحقق من وجود المنتج مسبقاً لتجنب التكرار وتحديثه أو إضافته
        product = Product.query.filter_by(name=title).first()
        
        if product:
            product.price = price
            product.description = description
        else:
            new_product = Product(
                name=title,
                price=price,
                description=description
            )
            db.session.add(new_product)
            saved_count += 1
                
    db.session.commit()
    return f"تمت المزامنة بنجاح! تم حفظ وتحديث المنتجات في قاعدة البيانات."
