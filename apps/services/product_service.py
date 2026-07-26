def get_all_products(self, input_data: dict = None) -> list:
    """جلب جميع المنتجات"""
    query = """
    query FindAllProducts {
        findAllProducts {
            success
            message
            data {
                qid
                title
                price
                status
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
        data = self.client.execute(query, operation_name="FindAllProducts")
        if data and "findAllProducts" in data:
            result = data["findAllProducts"]
            if result.get("success"):
                return result.get("data", [])
        return []
    except Exception as e:
        print(f"❌ [ProductService]: خطأ في جلب المنتجات: {e}")
        return []
