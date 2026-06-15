# 📂 apps/utils/products_engine.py
from .bridge_engine import QumraBridgeEngine
from apps.extensions import db
from apps.models.product_db import Product

class ProductsEngine(QumraBridgeEngine):
    def sync_products_to_db(self):
        query = """
        query {
            products(first: 20) {
                data {
                    qid
                    title
                    status
                    price
                    compareAtPrice
                    quantity
                    image
                    createdAt
                }
            }
        }
        """
        result = self.execute_query(query)
        data = result.get("data", {}).get("products", {}).get("data", [])
        
        count = 0
        for item in data:
            product = Product.query.filter_by(qid=item.get('qid')).first() or Product(qid=item.get('qid'))
            
            product.title = item.get('title')
            product.price = float(item.get('price', 0))
            product.compare_at_price = float(item.get('compareAtPrice', 0))
            product.quantity = int(item.get('quantity', 0))
            product.status = item.get('status')
            product.image_url = item.get('image')
            product.created_at = item.get('createdAt')
            
            db.session.add(product)
            count += 1
            
        db.session.commit()
        return count
