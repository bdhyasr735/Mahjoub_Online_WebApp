# 📂 apps/api/product_sync_engine.py

import logging
from apps.extensions import db
from apps.models.product_db import Product

logger = logging.getLogger(__name__)

class ProductSyncEngine:

    @staticmethod
    def process_products(products_data):
        """معالجة وتحديث قائمة المنتجات المجلوبة من قمرة."""
        if not products_data:
            return 0
            
        synced_count = 0
        for item in products_data:
            try:
                qid = str(item.get('_id'))
                product = Product.query.filter_by(qid=qid).first()
                
                # تحديث أو إنشاء
                if not product:
                    product = Product(qid=qid)
                    db.session.add(product)
                
                # تحديث الحقول الأساسية
                product.title = item.get('title', 'منتج غير معرف')
                product.sku = item.get('sku', 'N/A')
                product.cost_price = float(item.get('price', 0))
                
                synced_count += 1
            except Exception as e:
                logger.error(f"❌ خطأ في معالجة المنتج {item.get('_id')}: {e}")
                continue
        
        db.session.commit()
        return synced_count
