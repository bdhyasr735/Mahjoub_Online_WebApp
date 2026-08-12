import os
from graphql_client import GraphQLClient


class OrderService:

  def __init__(self, client: GraphQLClient = None):
    self.client = client or GraphQLClient()

  def fetch_orders(self, limit: int = 10, page: int = 1):
    """جلب قائمة الطلبات من متجر قمرة"""
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
    return data.get("findAllOrders", {}).get("data", [])

  def update_order_status(self, order_id: str, status: str):
    """تحديث حالة طلب معين في قمرة"""
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

  def sync_orders(self):
    """دالة المزامنة الرئيسية لربط البيانات وقراءتها"""
    print("بدء عملية مزامنة الطلبات...")
    orders = self.fetch_orders(limit=20, page=1)

    print(f"تم جلب {len(orders)} طلب من المتجر.")

    for order in orders:
      order_id = order.get("id")
      status = order.get("orderStatus")
      total = order.get("totalPrice")

      # أضف هنا منطق الإدراج أو التحديث الخاص بقاعدة بياناتك
      print(f"مزامنة الطلب [{order_id}] - الحالة: {status} - الإجمالي: {total}")

    print("تمت عملية المزامنة بنجاح.")


if __name__ == "__main__":
  # تجربة تشغيل المزامنة مباشرة
  service = OrderService()
  service.sync_orders()
