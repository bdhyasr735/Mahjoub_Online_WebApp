import os

# 1. إصلاح الاستيراد للعمل داخل حزمة Flask/Render وفي التشغيل المباشر
try:
  from .graphql_client import GraphQLClient
except ImportError:
  from graphql_client import GraphQLClient


class OrderService:

  def __init__(self, client: GraphQLClient = None):
    self.client = client or GraphQLClient()

  def fetch_orders(self, limit: int = 10, page: int = 1):
    """جلب قائمة الطلبات من API قمرة"""
    query = """
        query FindAllOrders($limit: Int, $page: Int) {
          findAllOrders(limit: $limit, page: $page) {
            data {
              id
              orderKey
              totalPrice
              orderStatus
              createdAt
            }
          }
        }
        """
    variables = {"limit": limit, "page": page}
    data = self.client.execute(query, variables)
    if data and "findAllOrders" in data:
      return data["findAllOrders"].get("data", [])
    return []

  # 2. إضافة الدالة التي يستدعيها ملف orders.py بنفس الاسم والبارامترات
  def get_all_orders(self, page: int = 1, limit: int = 10):
    return self.fetch_orders(limit=limit, page=page)

  def update_order_status(self, order_id: str, status: str):
    """تحديث حالة الطلب"""
    mutation = """
        mutation UpdateOrderStatus($input: UpdateOrderStatusInput!) {
          updateOrderStatus(input: $input) {
            success
            message
          }
        }
        """
    variables = {"input": {"orderId": order_id, "status": status}}
    return self.client.execute(mutation, variables)
