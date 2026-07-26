# coding: utf-8
# 📂 apps/services/order_service.py

from typing import Dict, Any, Optional, List
from .graphql_client import GraphQLClient


class OrderService:
    """خدمة إدارة الطلبات والمزامنة"""
    
    def __init__(self, client: GraphQLClient):
        self.client = client

    def get_order(self, qid: str) -> Optional[Dict[str, Any]]:
        """جلب تفاصيل الطلب باستخدام المعرف qid"""
        query = """
        query GetOrder($qid: ID!) {
            order(qid: $qid) {
                qid
                total
                status
                createdAt
                items {
                    productQid
                    quantity
                    price
                }
            }
        }
        """
        try:
            result = self.client.execute(query, {"qid": qid}, operation_name="GetOrder")
            return result.get('order') if result else None
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في جلب الطلب {qid}: {e}")
            return None

    def get_orders(self, input_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """جلب قائمة الطلبات مع إمكانية التصفية"""
        query = """
        query GetOrders($input: FindAllOrdersInput) {
            orders(input: $input) {
                qid
                total
                status
                createdAt
                items {
                    productQid
                    quantity
                    price
                }
            }
        }
        """
        variables = {"input": input_data} if input_data else {}
        try:
            result = self.client.execute(query, variables, operation_name="GetOrders")
            return result.get('orders', []) if result else []
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في جلب الطلبات: {e}")
            return []

    def create_order(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """إنشاء طلب جديد"""
        mutation = """
        mutation CreateOrder($input: OrderInput!) {
            createOrder(input: $input) {
                qid
                total
                status
            }
        }
        """
        try:
            result = self.client.execute(mutation, {"input": input_data}, operation_name="CreateOrder")
            return result.get('createOrder') if result else None
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في إنشاء الطلب: {e}")
            return None

    def update_order_status(self, qid: str, status: str) -> Optional[Dict[str, Any]]:
        """تحديث حالة الطلب"""
        mutation = """
        mutation UpdateOrderStatus($qid: ID!, $status: String!) {
            updateOrderStatus(qid: $qid, status: $status) {
                qid
                status
                updatedAt
            }
        }
        """
        try:
            result = self.client.execute(mutation, {"qid": qid, "status": status}, operation_name="UpdateOrderStatus")
            return result.get('updateOrderStatus') if result else None
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في تحديث حالة الطلب {qid}: {e}")
            return None

    def delete_order(self, qid: str) -> bool:
        """حذف طلب"""
        mutation = """
        mutation DeleteOrder($qid: ID!) {
            deleteOrder(qid: $qid)
        }
        """
        try:
            result = self.client.execute(mutation, {"qid": qid}, operation_name="DeleteOrder")
            return result.get('deleteOrder', False) if result else False
        except Exception as e:
            print(f"❌ [OrderService]: خطأ في حذف الطلب {qid}: {e}")
            return False
