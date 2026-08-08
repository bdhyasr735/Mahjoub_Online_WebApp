# coding: utf-8
# 📂 apps/services/order_service.py

from apps.services.graphql_client import GraphQLClient

class OrderService:
    def __init__(self, client=None):
        self.client = client if client else GraphQLClient()

    def get_all_orders(self, page: int = 1, limit: int = 50):
        # ✅ استعلام نظيف وآمن، يطلب فقط الحقول الموجودة والمؤكدة
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
        # ✅ استعلام نظيف وآمن للطلب الفردي
        query = """
        query FindOrderByIdBasic($id: ID!) {
            findOrderById(id: $id) {
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
                success
                message
            }
        }
        """
        try:
            data = self.client.execute(query, {"id": order_id})
            if data and "findOrderById" in data:
                return data["findOrderById"].get("data")
            return None
        except Exception as e:
            print(f"❌ [OrderService] خطأ في get_order_by_id: {e}")
            return None

    # ============================================================
    # 🚀 دالة تحديث الحالة في قمره (النسخة النهائية والمُصححة)
    # ============================================================
    def update_order_status_in_qumra(self, order_id: str, status_code: str) -> bool:
        """
        إرسال طلب تحديث الحالة إلى قمره عبر Mutation.
        """
        # ✅ خريطة تحويل حالات محجوب إلى معرفات الحالة (_id) في قمره (معتمدة رسمياً من الساندبوكس)
        qumra_status_id_map = {
            'pending': '68651b7d99fc8f5413cf6fe0',    # pending
            'processing': '68651b7d99fc8f5413cf6fe1', # preparing
            'shipped': '68651b7d99fc8f5413cf6fe2',    # shipped
            'delivered': '68651b7d99fc8f5413cf6fe3',  # delivered
            'completed': '68651b7d99fc8f5413cf6fe9',  # complete
            'cancelled': '68651b7d99fc8f5413cf6fe4',  # cancelled
            'refunded': '68651b7d99fc8f5413cf6fe8'    # returned
        }
        
        # الحصول على معرف الحالة الصحيح من القائمة
        target_status_id = qumra_status_id_map.get(status_code, '68651b7d99fc8f5413cf6fe0') # افتراضي: pending ID
        
        mutation = """
        mutation ChangeOrderStatus($changeOrderStatusInput2: ChangeOrderStatusInput!) {
            changeOrderStatus(input: $changeOrderStatusInput2) {
                success
                message
            }
        }
        """
        try:
            # ✅ التصحيح النهائي بناءً على تبويب Variables في الساندبوكس:
            # قمره تتطلب "id" و "status" (حيث status هو الـ _id للحالة)
            input_data = {
                "id": order_id,                 # معرف الطلب (مفتاح id وليس _id)
                "status": target_status_id      # معرف الحالة (الـ _id الخاص بـ preparing)
            }
            
            print(f"🚀 [DEBUG] إرسال الطلب إلى قمره: {input_data}")
            
            data = self.client.execute(mutation, {"changeOrderStatusInput2": input_data})
            
            if data and "changeOrderStatus" in data:
                return data["changeOrderStatus"].get("success", False)
            return False
        except Exception as e:
            print(f"❌ [OrderService] فشل تحديث الحالة في قمره: {e}")
            return False


# ============================================================
orders_service = OrderService()

def get_all_orders(page=1, limit=50):
    return orders_service.get_all_orders(page, limit)

def get_order_by_id(order_id):
    return orders_service.get_order_by_id(order_id)
