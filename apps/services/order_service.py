from graphql_client import GraphQLClient
from pathlib import Path

class OrderService:
    def __init__(self, client: GraphQLClient):
        self.client = client
        with open(Path(__file__).parent / "orders_queries.graphql") as f:
            self.queries = f.read()

    def get_order_by_id(self, order_id: str):
        query = """
        query FindOrderById($id: ID!) {
          findOrderById(id: $id) { ...OrderFull }
        }
        """
        variables = {"id": order_id}
        result = self.client.execute(query, variables)
        return result.get("data", {}).get("findOrderById", {})

    def get_all_orders(self, input_data: dict):
        query = """
        query FindAllOrders($input: FindAllOrdersInput!) {
          findAllOrders(input: $input) {
            data { ...OrderSummary }
            pagination { totalItems totalPages currentPage limit hasNextPage }
          }
        }
        """
        variables = {"input": input_data}
        result = self.client.execute(query, variables)
        return result.get("data", {}).get("findAllOrders", {})
