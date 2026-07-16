# coding: utf-8
# 📂 apps/api/sync_engine.py

import logging
from apps.extensions import db
from apps.models.product_db import Product

logger = logging.getLogger(__name__)

class ProductSyncEngine:

    @staticmethod
    def process_products(products_data):
        """معالجة وتحديث قائمة المنتجات المجلوبة من قمرة."""
        if not products_data or not isinstance(products_data, list):
            logger.warning("❌ لم يتم استقبال بيانات صالحة للمزامنة.")
            return 0
            
        synced_count = 0
        for item in products_data:
            try:
                # استخدام qid القادم من Apollo GraphQL
                qid = str(item.get('qid'))
                product = Product.query.filter_by(qid=qid).first()
                
                # إنشاء إذا لم يوجد
                if not product:
                    product = Product(qid=qid)
                    db.session.add(product)
                
                # تحديث الحقول المباشرة
                product.title = item.get('title', 'منتج غير معرف')
                
                # استخراج البيانات من الحقول المتداخلة (Nested Fields)
                pricing = item.get('pricing', {}) or {}
                identification = item.get('identification', {}) or {}
                
                # معالجة آمنة للسعر
                try:
                    product.cost_price = float(pricing.get('price', 0))
                except (ValueError, TypeError):
                    product.cost_price = 0.0
                
                # تحديث الـ SKU
                product.sku = identification.get('sku', 'N/A')
                
                synced_count += 1
            except Exception as e:
                logger.error(f"❌ خطأ في معالجة المنتج {item.get('qid', 'unknown')}: {e}")
                continue
        
        try:
            db.session.commit()
            return synced_count
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ فشل عملية حفظ البيانات في قاعدة البيانات: {e}")
            return 0
