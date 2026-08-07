# coding: utf-8
# 📂 apps/services/order_service.py

from apps.services.graphql_client import GraphQLClient

class OrderService:
    def __init__(self, client=None):
        self.client = client if client else GraphQLClient()

    def get_all_orders(self, page: int = 1, limit: int = 50):
        # ✅ تم تصحيح pagination.totalCount إلى totalItems
        query = """
        query GetOrders($page: Int, $limit: Int) {
            findAllOrders(input: { page: $page, limit: $limit }) {
                data {
                    _id
                    totalPrice
                    isPaid
                    createdAt
                    status {
                        code
                        title
                    }
                    account {
                        fullname    # ⚠️ قد تحتاج لتغييرها إلى name أو fullName حسب الساندبوكس
                        phone       # ⚠️ قد تحتاج لتغييرها إلى phoneNumber أو mobile
                    }
                    shippingAddress {
                        street
                        description
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
                    totalItems   # ✅ تم التصحيح هنا (بدلاً من totalCount)
                }
            }
        }
        """
        try:
            data = self.client.execute(query, {"page": page, "limit": limit})
            if data and isinstance(data, dict) and "findAllOrders" in data:
                return data["findAllOrders"]
            return {"data": [], "pagination": {"hasNextPage": False, "totalItems": 0}}
        except Exception as e:
            print(f"❌ [OrderService] خطأ في get_all_orders: {e}")
            return {"data": [], "pagination": {"hasNextPage": False, "totalItems": 0}}

    def get_order_by_id(self, order_id: str):
        query = """
        query GetOrder($id: String!) {
            findOrderByQid(qid: $id) {
                _id
                totalPrice
                isPaid
                createdAt
                status {
                    code
                    title
                }
                account {
                    fullname
                    phone
                }
                shippingAddress {
                    street
                    description
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
            if data and "findOrderByQid" in data:
                return data["findOrderByQid"]
            return None
        except Exception as e:
            print(f"❌ [OrderService] خطأ في get_order_by_id: {e}")
            return None

orders_service = OrderService()

def get_all_orders(page=1, limit=50):
    return orders_service.get_all_orders(page, limit)

def get_order_by_id(order_id):
    return orders_service.get_order_by_id(order_id)
