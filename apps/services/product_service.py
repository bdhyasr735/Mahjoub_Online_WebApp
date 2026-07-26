def get_all_products(self, input_data: dict = None) -> list:
    """جلب جميع المنتجات"""
    query = """
    query {
        __schema {
            types {
                name
            }
        }
    }
    """
    try:
        data = self.client.execute(query)
        if data and "__schema" in data:
            return data["__schema"]["types"]
        return []
    except Exception as e:
        print(f"❌ [ProductService]: خطأ في جلب المنتجات: {e}")
        return []
