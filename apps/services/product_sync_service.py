# coding: utf-8
# 📂 apps/services/product_sync_service.py

import requests

# ✅ الرابط الصحيح للـ GraphQL API
GRAPHQL_ENDPOINT = "https://mahjoub.online/admin/graphql"

class ProductSyncService:
    def __init__(self, token: str):
        # ترويسات الطلب مع تمرير التوكن بصيغة Bearer
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def fetch_products(self, page: int = 1, limit: int = 20):
        query = """
        query($page: Int!, $limit: Int!) {
          findAllProducts(input: { page: $page, limit: $limit }) {
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

            # 🛡️ تحقق قبل الوصول إلى result["data"]
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
        query = """
        query($qid: String!) {
          findProductByQid(qid: $qid) {
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
          }
        }
        """
        variables = {"qid": qid}
        
        try:
            response = requests.post(
                GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={"query": query, "variables": variables},
                timeout=30
            )

            if response.status_code != 200:
                print(f"HTTP Error Status: {response.status_code}")
                return None

            result = response.json()

            # 🛡️ تحقق قبل الوصول إلى result["data"]
            if "errors" in result:
                print("GraphQL Error:", result["errors"])
                return None
                
            if "data" not in result or "findProductByQid" not in result["data"]:
                print("Unexpected response:", result)
                return None

            return result["data"]["findProductByQid"]

        except requests.exceptions.RequestException as e:
            print(f"Network Connection Error: {e}")
            return None

    def sync_to_local_db(self, products_data):
        if not products_data or "data" not in products_data:
            print("No products found to sync.")
            return

        for product in products_data.get("data", []):
            print(f"Fetched product {product.get('qid')} - {product.get('title')}")
        print("Sync completed (no local save).")
