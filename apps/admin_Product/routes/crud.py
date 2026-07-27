def update_product_data(self, input_data: dict) -> dict:
    query = """
    mutation UpdateProduct($input: UpdateProductInput!) {
        updateProduct(input: $input) {
            success
            message
            data {
                qid
                title
                pricing {
                    price
                    compareAtPrice
                }
                status
            }
        }
    }
    """
    try:
        data = self.client.execute(query, {"input": input_data})
        if data and "updateProduct" in data:
            result = data["updateProduct"]
            if result.get("success"):
                return result.get("data", {})
        return {}
    except Exception as e:
        print(f"❌ [ProductService]: {e}")
        return {}
