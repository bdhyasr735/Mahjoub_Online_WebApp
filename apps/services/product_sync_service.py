# apps/services/product_sync_service.py
# coding: utf-8

import uuid
import logging
from apps.extensions import db
from apps.models.product_db import Product
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.services.graphql_client import QomrahGraphQLClient

def sync_products_from_qomra():
    """
    جلب كافة المنتجات تدريجياً عبر نظام الترقيم الصفحي (Pagination) من منصة قمرة 
    وتخزينها وتحديثها محلياً مع ربطها بجدول الموردين السيادي وضمان استخراج الأسعار بدقة تامة.
    """
    page = 1
    limit = 100
    all_products_data = []
    
    # حلقة تكرارية لجلب كافة الصفحات من واجهة قمرة حتى استنفاد جميع المنتجات (~46 صفحة فأكثر)
    while True:
        query = """
        query GetAllProductsUnified($page: Int, $limit: Int) {
          findAllProducts(page: $page, limit: $limit) {
            qid
            title
            name
            description
            quantity
            price
            salePrice
            images {
              _id
              fileUrl
              url
              path
            }
            pricing {
              price
              originalPrice
              salePrice
              amount
            }
          }
        }
        """
        
        variables = {'page': page, 'limit': limit}
        
        try:
            result = QomrahGraphQLClient.execute_query(query, variables=variables)
        except Exception as e:
            # طريقة بديلة في حال لم يدعم العميل تمرير الـ variables بشكل مباشر
            try:
                raw_query = f"""
                query GetAllProductsUnified {{
                  findAllProducts(page: {page}, limit: {limit}) {{
                    qid
                    title
                    name
                    description
                    quantity
                    price
                    salePrice
                    images {{
                      _id
                      fileUrl
                      url
                      path
                    }}
                    pricing {{
                      price
                      originalPrice
                      salePrice
                      amount
                    }}
                  }}
                }}
                """
                result = QomrahGraphQLClient.execute_query(raw_query)
            except Exception as inner_e:
                logging.error(f"❌ خطأ أثناء تنفيذ استعلام المزامنة للصفحة {page}: {inner_e}")
                raise Exception(f"فشل الاتصال بخدمة قمرة في الصفحة {page}: {str(inner_e)}")

        if not result:
            break

        # استخراج البيانات بمرونة لجميع الهياكل المحتملة للاستجابة
        response_data = result.get('data', result)
        products_data = []

        if isinstance(response_data, dict):
            find_all = response_data.get('findAllProducts') or response_data.get('data') or response_data
            if isinstance(find_all, dict):
                products_data = find_all.get('data') or find_all.get('items') or find_all.get('results') or []
            elif isinstance(find_all, list):
                products_data = find_all
        elif isinstance(response_data, list):
            products_data = response_data

        if not products_data:
            break

        all_products_data.extend(products_data)
        
        # إذا كان عدد المنتجات المسترجعة أقل من الحد الأقصى للصفحة، فهذا يعني وصولنا لآخر صفحة
        if len(products_data) < limit:
            break
            
        page += 1
        # حماية أمان ضد الحلقات اللانهائية
        if page > 200:
            break

    logging.info(f"📦 [Total Parsed Products from Qomra Across All Pages]: {len(all_products_data)}")

    if not all_products_data:
        return "تمت المزامنة بنجاح، لكن منصة قمرة لم تقم بإرجاع أي منتجات."

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

    for item in all_products_data:
        if not isinstance(item, dict):
            continue
            
        title = item.get('title') or item.get('name')
        if not title:
            continue
            
        qid = item.get('qid') or item.get('_id') or item.get('id')
        description = item.get('description', '')
        
        try:
            quantity = int(item.get('quantity', 0) or 0)
        except (ValueError, TypeError):
            quantity = 0
        
        # استخراج الصورة مع دعم كافة المفاتيح المحتملة
        images = item.get('images', [])
        image_url = None
        if images and isinstance(images, list):
            first_img = images[0]
            if isinstance(first_img, dict):
                image_url = first_img.get('fileUrl') or first_img.get('url') or first_img.get('path')
            elif isinstance(first_img, str):
                image_url = first_img
        
        # استخراج السعر والعملة بدقة من كائن pricing أو الحقول المباشرة لمنع ظهور القيمة صفر
        price_val = 0
        currency = 'SAR'
        
        pricing = item.get('pricing')
        if isinstance(pricing, dict):
            price_val = (
                pricing.get('price') or 
                pricing.get('salePrice') or 
                pricing.get('originalPrice') or 
                pricing.get('amount') or 0
            )
        elif isinstance(pricing, (int, float, str)):
            price_val = pricing

        if not price_val or float(price_val or 0) == 0:
            price_val = (
                item.get('price') or 
                item.get('salePrice') or 
                item.get('originalPrice') or 0
            )

        try:
            price = float(price_val or 0)
        except (ValueError, TypeError):
            price = 0.0

        product_qid_str = str(qid) if qid else f"qomra_{uuid.uuid4().hex[:8]}"

        # 1. حفظ أو تحديث المنتج في جدول المنتجات المحلي
        product = None
        if qid:
            product = Product.query.filter_by(qid=str(qid)).first()
        if not product:
            product = Product.query.filter_by(title=title).first()
            
        if product:
            product.qid = product_qid_str
            product.title = title
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
                title=title,
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
    
    return f"تمت المزامنة بنجاح! تم جلب ومعالجة {len(all_products_data)} منتج عبر جميع الصفحات: إضافة {saved_count}، تحديث {updated_count}، وربط {mappings_count} منتج."
