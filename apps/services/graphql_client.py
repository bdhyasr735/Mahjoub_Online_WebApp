import os
import requests


class GraphQLClient:

  def __init__(self, endpoint=None, token=None):
    self.endpoint = endpoint or os.getenv(
        "QUMRA_ENDPOINT", "https://api.qumra.cloud/graphql"
    )
    # جلب التوكين من بيئة Render أو استخدام المفتاح المباشر
    raw_token = token or os.getenv(
        "QUMRA_TOKEN", "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"
    )
    self.token = raw_token.strip() if raw_token else ""

  def execute(self, query: str, variables: dict = None):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {self.token}",
    }

    payload = {"query": query, "variables": variables or {}}

    try:
      response = requests.post(
          self.endpoint, json=payload, headers=headers, timeout=15
      )

      # طباعة رمز الاستجابة للتأكد من حالة التوثيق
      if response.status_code == 500 or response.status_code == 401:
        print(
            f"❌ [Qumra Response Error] HTTP {response.status_code}:"
            f" {response.text}"
        )
        return None

      response.raise_for_status()
      result = response.json()

      if "errors" in result:
        print(f"❌ [Qumra GraphQL Error]: {result['errors']}")
        return None

      return result.get("data")

    except Exception as e:
      print(f"❌ [Qumra Request Exception]: {e}")
      return None
