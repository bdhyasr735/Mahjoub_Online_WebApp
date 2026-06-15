# 📂 apps/utils/products_engine.py
import logging
from apps.utils.bridge_engine import QumraBridgeEngine
from apps.extensions import db
from apps.models.product_db import Product  # تأكد من وجود هذا الموديل

logger = logging.getLogger(__name__)

class ProductsEngine(QumraBridgeEngine):
    def __init__(self):
        super().__init__()

    def sync_products_to_db(self):
        """جلب المنتجات وحفظها في قاعدة البيانات"""
        query = """
        query {
            findAllProducts {
                title
                pricing { price }
                quantity
                status
                images { fileUrl }
            }
        }
        """
        result = self.execute_query(query)
        
        if not result or 'data' not in result:
            logger.error("فشل جلب المنتجات من قمرة")
            return 0

        raw_products = result.get('data', {}).get('findAllProducts', [])
        count = 0
        
        for p in raw_products:
            # استخدام العنوان كمعرف فريد (أو عدل حسب المعرف المتوفر لديك)
            title = p.get('title', 'بدون اسم')
            product = Product.query.filter_by(title=title).first() or Product(title=title)
            
            # تحديث البيانات
            product.price = p.get('pricing', {}).get('price', 0)
            product.quantity = p.get('quantity', 0)
            product.status = p.get('status', 'غير محدد')
            
            images = p.get('images', [])
            product.image_url = images[0].get('fileUrl') if images else 'https://via.placeholder.com/150'
            
            db.session.add(product)
            count += 1
            
        db.session.commit()
        logger.info(f"تمت مزامنة {count} منتج بنجاح.")
        return count

    def fetch_all(self, search_term="", page=1):
        """إرجاع قائمة المنتجات للعرض (مع الترقيم والفلترة)"""
        products = Product.query.all()
        all_products = []
        for p in products:
            all_products.append({
                "title": p.title,
                "price": p.price,
                "quantity": p.quantity,
                "image_url": p.image_url,
                "status": p.status
            })
            
        if search_term:
            all_products = [p for p in all_products if search_term.lower() in p['title'].lower()]
            
        per_page = 20
        start = (page - 1) * per_page
        return all_products[start:start + per_page]
