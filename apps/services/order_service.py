# coding: utf-8
# 📂 apps/services/order_service.py

from apps.services.graphql_client import GraphQLClient

class OrderService:
    def __init__(self, client=None):
        self.client = client if client else GraphQLClient()

    def get_all_orders(self, page: int = 1, limit: int = 50):
        # ✅ نهائياً، لا نطلب أي حقول غير موجودة (orderId, orderNumber, etc)
        query = """
        query FindAllOrdersBasic($input: FindAllOrdersInput!) {
            findAllOrders(input: $input) {
                data {
                    _id
                    type
                    totalPrice
                    isPaid
                    createdAt
                    status {
                        code
                        title
                    }
                    account {
                        account {
                            fullname
                            phone
                        }
                    }
                    items {
                        productId
                        quantity
                        price
                        productData {
                            title
                            price
                            image {
                                fileUrl
                            }
                        }
                    }
                }
                pagination {
                    totalItems
                    totalPages
                    currentPage
                    limit
                    hasNextPage
                }
            }
        }
        """
        try:
            data = self.client.execute(query, {"input": {"page": page, "limit": limit}})
            if data and isinstance(data, dict) and "findAllOrders" in data:
                return data["findAllOrders"]
            return {"data": [], "pagination": {"totalItems": 0, "hasNextPage": False}}
        except Exception as e:
            print(f"❌ [OrderService] خطأ في get_all_orders: {e}")
            return {"data": [], "pagination": {"totalItems": 0, "hasNextPage": False}}

    def get_order_by_id(self, order_id: str):
        query = """
        query FindOrderByIdBasic($id: ID!) {
            findOrderById(id: $id) {
                _id
                type
                totalPrice
                isPaid
                createdAt
                status {
                    code
                    title
                }
                account {
                    account {
                        fullname
                        phone
                    }
                }
                items {
                    productId
                    quantity
                    price
                    productData {
                        title
                        price
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
            if data and "findOrderById" in data:
                return data["findOrderById"]
            return None
        except Exception as e:
            print(f"❌ [OrderService] خطأ في get_order_by_id: {e}")
            return None

orders_service = OrderService()
def get_all_orders(page=1, limit=50):
    return orders_service.get_all_orders(page, limit)
def get_order_by_id(order_id):
    return orders_service.get_order_by_id(order_id)
