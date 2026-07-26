def get_all_products(self, input_data: dict = None) -> list:
    """جلب جميع المنتجات"""
    query = """
    query {
        findAllProducts {
            success
            message
            data {
                qid
                title
                price
                status
            }
        }
    }
    """
    try:
        data = self.client.execute(query)
        if data and "findAllProducts" in data:
            result = data["findAllProducts"]
            if result.get("success"):
                return result.get("data", [])
        return []
    except Exception as e:
        print(f"❌ [ProductService]: {e}")
        return []
