# coding: utf-8
# 📂 apps/services/order_service.py
# خدمة جلب الطلبات - تعتمد على GraphQLClient الخاص بـ Qumra

from apps.services.graphql_client import GraphQLClient

class OrderService:
    """خدمة إدارة الطلبات (تستخدم نفس عميل GraphQL الخاص بالمنتجات)"""

    def __init__(self, client=None):
        # ✅ استخدام نفس الـ Client تماماً الموجود في graphql_client.py
        self.client = client if client else GraphQLClient()

    def get_all_orders(self, page: int = 1, limit: int = 50):
        """
        جلب الطلبات من المصدر الخارجي عبر نفس الرابط الذي تعمل به المنتجات.
        """
        query = """
        query GetOrders($page: Int, $limit: Int) {
            orders(page: $page, limit: $limit) {
                data {
                    _id
                    orderNumber
                    orderReference
                    totalPrice
                    isPaid
                    createdAt
                    updatedAt
                    account {
                        account {
                            fullname
                            phone
                        }
                    }
                    shippingAddress {
                        street
                        description
                    }
                    status {
                        code
                        title
                    }
                    items {
                        productId
                        quantity
                        price
                        productData {
                            title
                            image {
                                fileUrl
                            }
                        }
                    }
                }
                pagination {
                    hasNextPage
                    totalCount
                }
            }
        }
        """
        try:
            # ✅ استخدام self.client.execute فقط، الرابط والـ Token موجودان داخلياً
            data = self.client.execute(query, {"page": page, "limit": limit})
            
            if data and isinstance(data, dict) and "orders" in data:
                return data["orders"]
            
            return {"data": [], "pagination": {"hasNextPage": False, "totalCount": 0}}

        except Exception as e:
            print(f"❌ [OrderService] خطأ في get_all_orders: {e}")
            return {"data": [], "pagination": {"hasNextPage": False, "totalCount": 0}}

    def get_order_by_id(self, order_id: str):
        """جلب طلب محدد بواسطة ID"""
        query = """
        query GetOrder($id: ID!) {
            order(id: $id) {
                _id
                orderNumber
                orderReference
                totalPrice
                isPaid
                createdAt
                updatedAt
                account {
                    account {
                        fullname
                        phone
                    }
                }
                shippingAddress {
                    street
                    description
                }
                status {
                    code
                    title
                }
                items {
                    productId
                    quantity
                    price
                    productData {
                        title
                        image {
                            fileUrl
                        }
                    }
                }
            }
        }
        """
        try:
            data = self.client.execute(query, {"id": order_id})
            if data and "order" in data:
                return data["order"]
            return None
        except Exception as e:
            print(f"❌ [OrderService] خطأ في get_order_by_id: {e}")
            return None

# ✅ تعريف المتغير العام للاستخدام
orders_service = OrderService()

# الدوال المباشرة للاستيراد من باقي الملفات
def get_all_orders(page=1, limit=50):
    return orders_service.get_all_orders(page, limit)

def get_order_by_id(order_id):
    return orders_service.get_order_by_id(order_id)
