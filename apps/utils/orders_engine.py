# 📂 apps/utils/orders_engine.py
from apps.utils.bridge_engine import QumraBridgeEngine
import logging

logger = logging.getLogger(__name__)

class OrdersEngine(QumraBridgeEngine):
    def fetch_all_orders(self, page=1):
        """
        جلب قائمة الطلبات باستخدام حقول الطلب الأساسية.
        """
        query = """
        query {
            findAllOrders {
                orderId
                status
                total
                createdAt
                customer {
                    name
                    phone
                }
                items {
                    title
                    qty
                    subtotal
                }
                shipping {
                    city
                    street
                }
            }
        }
        """
        result = self.execute_query(query)
        
        if not result or 'data' not in result:
            return []

        raw_orders = result.get('data', {}).get('findAllOrders', [])
        
        # معالجة وتنسيق بيانات الطلبات
        processed_orders = []
        for o in raw_orders:
            processed_orders.append({
                "orderId": o.get('orderId'),
                "status": o.get('status'),
                "total": o.get('total', 0),
                "date": o.get('createdAt'),
                "customerName": o.get('customer', {}).get('name', 'غير معروف'),
                "customerPhone": o.get('customer', {}).get('phone', '-'),
                "itemsCount": len(o.get('items', [])),
                "shippingCity": o.get('shipping', {}).get('city', '-')
            })
            
        return processed_orders

    def get_financial_summary(self):
        """
        استعلام مخصص للحقول المالية التحليلية
        """
        query = """
        query {
            findAllOrders {
                totalPriceWithTax
                taxAmount
                shippingPrice
                paymentType
                financialStatus
            }
        }
        """
        return self.execute_query(query)
