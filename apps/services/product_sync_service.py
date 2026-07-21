# coding: utf-8
# 📂 apps/services/product_sync_service.py

import requests
from apps.services.fetch_product_data import GET_PRODUCT_DETAIL_QUERY

GRAPHQL_ENDPOINT = "https://mahjoub.online/admin/graphql"

class ProductSyncService:
    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def fetch_products(self, page: int = 1, limit: int = 20, title: str = ""):
        # استعلام GraphQL المدعوم بالكامل مع متغير البحث title ومعاملات التصفح
        query = """
        query($page: Int!, $limit: Int!, $title: String) {
          findAllProducts(input: { page: $page, limit: $limit, title: $title }) {
            success
            message
            data {
              qid
              title
              description
              pricing { price }
              quantity
              images { fileUrl }
            }
            pagination {
              totalPages
              currentPage
              limit
            }
          }
        }
        """

        variables = {"page": page, "limit": limit}
        if title:
            variables["title"] = title
        
        try:
            response = requests.post(
                GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={"query": query, "variables": variables},
                timeout=30
            )

            if response.status_code != 200:
                print(f"HTTP Error Status: {response.status_code}")
                return {"data": [], "pagination": None}

            result = response.json()

            if "errors" in result:
                print("GraphQL Error:", result["errors"])
                return {"data": [], "pagination": None}
                
            if "data" not in result or "findAllProducts" not in result["data"]:
                print("Unexpected response:", result)
                return {"data": [], "pagination": None}

            return result["data"]["findAllProducts"]

        except requests.exceptions.RequestException as e:
            print(f"Network Connection Error: {e}")
            return {"data": [], "pagination": None}

    def fetch_product_by_qid(self, qid: str):
        # استخدام الاستعلام الشامل المستورد من ملف fetch_product_data
        variables = {"qid": qid}
        
        try:
            response = requests.post(
                GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={"query": GET_PRODUCT_DETAIL_QUERY, "variables": variables},
                timeout=30
            )

            if response.status_code != 200:
                return None

            result = response.json()
            if "errors" in result or "data" not in result or "findProductByQid" not in result["data"]:
                return None

            # إرجاع بيانات المنتج التفصيلية المضمنة بالداخل
            res_data = result["data"]["findProductByQid"]
            if res_data and res_data.get("success"):
                return res_data.get("data")
            
            return None
        except requests.exceptions.RequestException:
            return None

    def sync_to_local_db(self, products_data):
        if not products_data or "data" not in products_data:
            print("No products found to sync.")
            return

        for product in products_data.get("data", []):
            print(f"Fetched product {product.get('qid')} - {product.get('title')}")
        print("Sync completed.")
