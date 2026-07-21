# coding: utf-8
# 📂 apps/services/product_sync_service.py

import requests
from apps.services.update_product_data import UPDATE_PRODUCT_MUTATION

GRAPHQL_ENDPOINT = "https://mahjoub.online/admin/graphql"

# الاستعلام الشامل لتفاصيل المنتج مصححاً حسب مخطط الـ GraphQL الفعلي
GET_PRODUCT_DETAIL_QUERY = """
query($qid: String!) {
  findProductByQid(qid: $qid) {
    success
    message
    data {
      qid
      title
      slug
      description
      status
      quantity
      pricing {
        price
        compareAtPrice
      }
      images {
        fileUrl
      }
      variants {
        pricing {
          price
        }
        quantity
      }
    }
  }
}
"""

class ProductSyncService:
    def __init__(self, token: str):
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def fetch_products(self, page: int = 1, limit: int = 20, title: str = ""):
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
                print(f"findAllProducts HTTP Error {response.status_code}: {response.text}")
                return {"data": [], "pagination": None}

            result = response.json()
            if "errors" in result or "data" not in result or "findAllProducts" not in result["data"]:
                print(f"findAllProducts GraphQL Errors/Missing Data: {result}")
                return {"data": [], "pagination": None}

            return result["data"]["findAllProducts"]
        except requests.exceptions.RequestException as e:
            print(f"Request Exception in fetch_products: {str(e)}")
            return {"data": [], "pagination": None}

    def fetch_product_by_qid(self, qid: str):
        variables = {"qid": qid}
        try:
            response = requests.post(
                GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={"query": GET_PRODUCT_DETAIL_QUERY, "variables": variables},
                timeout=30
            )

            if response.status_code != 200:
                print(f"GraphQL HTTP Error: {response.status_code}")
                print(f"Response Body: {response.text}")
                return None

            result = response.json()
             
            # طباعة الأخطاء البرمجية للـ GraphQL إن وجدت
            if "errors" in result:
                print("GraphQL Errors in fetch_product_by_qid:", result["errors"])
                return None

            if "data" not in result or "findProductByQid" not in result["data"]:
                print("GraphQL Response missing data fields:", result)
                return None

            res_data = result["data"]["findProductByQid"]
            if res_data and res_data.get("success"):
                return res_data.get("data")
             
            print("GraphQL findProductByQid returned success=False:", res_data)
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request Exception in fetch_product_by_qid: {str(e)}")
            return None

    def update_product_data(self, qid: str, info: dict, pricing: dict, dims: dict, weight: dict, ident: dict, desc: str):
        variables = {
            "id": qid,
            "info": info,
            "pricing": pricing,
            "dims": dims,
            "weight": weight,
            "ident": ident,
            "desc": desc
        }
         
        try:
            response = requests.post(
                GRAPHQL_ENDPOINT,
                headers=self.headers,
                json={"query": UPDATE_PRODUCT_MUTATION, "variables": variables},
                timeout=30
            )

            if response.status_code != 200:
                print(f"Update HTTP Error {response.status_code}: {response.text}")
                return False

            result = response.json()
            if "errors" in result:
                print("Update Errors:", result["errors"])
                return False

            return True
        except requests.exceptions.RequestException as e:
            print(f"Request Exception in update_product_data: {str(e)}")
            return False

    def sync_to_local_db(self, products_data):
        if not products_data or "data" not in products_data:
            return
        for product in products_data.get("data", []):
            print(f"Fetched product {product.get('qid')} - {product.get('title')}")
