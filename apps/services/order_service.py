# order_service.py
class OrderService:
    def __init__(self, graphql_client):
        self.client = graphql_client

    def get_order(self, order_id):
        query = """
        query GetOrder($id: ID!) {
            order(id: $id) { id total items { productId quantity } }
        }
        """
        return self.client.execute(query, {"id": order_id})

    def create_order(self, input_data):
        mutation = """
        mutation CreateOrder($input: OrderInput!) {
            createOrder(input: $input) { id total }
        }
        """
        return self.client.execute(mutation, {"input": input_data})
