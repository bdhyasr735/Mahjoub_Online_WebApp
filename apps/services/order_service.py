# coding: utf-8
# 📂 apps/services/order_service.py

from apps.services.graphql_client import GraphQLClient

class OrderService:
    """خدمة إدارة الطلبات - تعتمد على GraphQLClient الخاص بـ Qumra"""

    def __init__(self, client=None):
        self.client = client if client else GraphQLClient()

    def get_all_orders(self, page: int = 1, limit: int = 50):
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
            data = self.client.execute(query, {"page": page, "limit": limit})
            if data and isinstance(data, dict) and "orders" in data:
                return data["orders"]
            return {"data": [], "pagination": {"hasNextPage": False, "totalCount": 0}}
        except Exception as e:
            print(f"❌ [OrderService] خطأ في get_all_orders: {e}")
            return {"data": [], "pagination": {"hasNextPage": False, "totalCount": 0}}

    def get_order_by_id(self, order_id: str):
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

# ✅ تعريف المتغير العام
orders_service = OrderService()

def get_all_orders(page=1, limit=50):
    return orders_service.get_all_orders(page, limit)

def get_order_by_id(order_id):
    return orders_service.get_order_by_id(order_id)
