# coding: utf-8
# 📂 apps/services/product_sync_service.py

import requests

# ✅ الرابط الصحيح للـ GraphQL API
GRAPHQL_ENDPOINT = "https://mahjoub.online/admin/graphql"

class ProductSyncService:
    def __init__(self, token: str):
        # ضع التوكن الحقيقي هنا (Bearer ...)
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
              id
              qid
              title
              description
              pricing { price }
              quantity
              images { fileUrl }
            }
            currency {
              code
              symbol
            }
            pagination {
              total
              page
              limit
              totalPages
              currentPage
            }
          }
        }
        """

        variables = {"page": page, "limit": limit}
        response = requests.post(
            GRAPHQL_ENDPOINT,
            headers=self.headers,
            json={"query": query, "variables": variables}
        )

        result = response.json()

        # 🛡️ تحقق قبل الوصول إلى result["data"]
        if "errors" in result:
            print("GraphQL Error:", result["errors"])
            return {"data": [], "pagination": None}
        if "data" not in result or "findAllProducts" not in result["data"]:
            print("Unexpected response:", result)
            return {"data": [], "pagination": None}

        return result["data"]["findAllProducts"]

    def fetch_product_by_qid(self, qid: str):
        query = """
        query($qid: String!) {
          findProductByQid(qid: $qid) {
            success
            message
            data {
              id
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
        response = requests.post(
            GRAPHQL_ENDPOINT,
            headers=self.headers,
            json={"query": query, "variables": variables}
        )

        result = response.json()

        # 🛡️ تحقق قبل الوصول إلى result["data"]
        if "errors" in result:
            print("GraphQL Error:", result["errors"])
            return None
        if "data" not in result or "findProductByQid" not in result["data"]:
            print("Unexpected response:", result)
            return None

        return result["data"]["findProductByQid"]

    def sync_to_local_db(self, products_data):
        # لا نقوم بأي حفظ داخلي، فقط نطبع للتأكيد
        for product in products_data.get("data", []):
            print(f"Fetched product {product.get('id')} - {product.get('title')}")
        print("Sync completed (no local save).")
