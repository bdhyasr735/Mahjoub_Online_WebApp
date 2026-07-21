# coding: utf-8
# 📂 apps/services/product_sync_service.py

import os
import requests
import logging
from apps.extensions import db
from apps.models.product_db import Product

logger = logging.getLogger(__name__)

# رابط وبوابة API الخاصة بقمرة
QOMRA_GRAPHQL_URL = os.getenv("QOMRA_GRAPHQL_URL", "https://api.qumra.cloud/graphql")
QOMRA_API_TOKEN = os.getenv("QOMRA_API_TOKEN", "")

# ✅ الاستعلام المصحح المتوافق تماماً مع Schema قمرة
PRODUCTS_QUERY = """
query GetProducts {
    products {
        id
        title
        description
        sku
        quantity
        pricing {
            price
        }
        images {
            url
        }
    }
}
"""

def sync_products_from_qomra():
    """
    جلب المنتجات من قمرة وتحديثها أو إضافتها في قاعدة البيانات المحلية.
    """
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {QOMRA_API_TOKEN}" if QOMRA_API_TOKEN else ""
    }

    try:
        response = requests.post(
            QOMRA_GRAPHQL_URL,
            json={"query": PRODUCTS_QUERY},
            headers=headers,
            timeout=15
        )
        
        # التأكد من وصول الاستجابة بنجاح
        if response.status_code != 200:
            logger.error(f"❌ Qomra Sync Failed [Status {response.status_code}]: {response.text}")
            raise Exception(f"فشل الاتصال بقمرة (رمز الاستجابة: {response.status_code})")

        payload = response.json()

        # معالجة أخطاء GraphQL في حال وجودها
        if "errors" in payload:
            logger.error(f"❌ GraphQL Validation Error: {payload['errors']}")
            raise Exception("حدث خطأ في استعلام قمرة (GraphQL Validation Error)")

        products_data = payload.get("data", {}).get("products", [])
        synced_count = 0

        for item in products_data:
            qid = str(item.get("id"))
            if not qid:
                continue

            # 1. استخراج السعر بأمان من كائن pricing
            pricing_data = item.get("pricing") or {}
            price = float(pricing_data.get("price") or 0.0)

            # 2. استخراج الصورة الأولى بأمان من قائمة images { url }
            images_list = item.get("images") or []
            image_url = ""
            if images_list and isinstance(images_list, list):
                image_url = images_list[0].get("url", "")

            # 3. تحديث المنتج إذا كان موجوداً أو إنشاء منتج جديد
            product = Product.query.filter_by(qid=qid).first()
            if not product:
                product = Product(qid=qid)
                db.session.add(product)

            product.title = item.get("title") or "منتج بدون اسم"
            product.description = item.get("description", "")
            product.sku = item.get("sku", "")
            product.quantity = int(item.get("quantity") or 0)
            product.price = price
            product.currency = "SAR"  # تعيين العملة افتراضياً للريال السعودي
            product.image_url = image_url

            synced_count += 1

        db.session.commit()
        logger.info(f"✅ Successfully synced {synced_count} products from Qomra.")
        return f"تمت مزامنة {synced_count} منتج بنجاح من قمرة."

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Error during Qomra sync: {str(e)}", exc_info=True)
        raise e
