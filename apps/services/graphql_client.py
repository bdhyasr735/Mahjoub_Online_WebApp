# coding: utf-8
# 📂 apps/services/graphql_client.py

import os
import logging
import requests

logger = logging.getLogger(__name__)

class GraphQLClient:
    def __init__(self, endpoint=None, api_key=None, timeout=30):
        self.endpoint = endpoint or os.getenv("GRAPHQL_ENDPOINT", "https://api.qumra.cloud/graphql")
        self.api_key = api_key or os.getenv("QUMRA_API_KEY", "")
        self.timeout = timeout
        self.session = requests.Session()

    def _get_headers(self):
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def execute(self, query, variables=None, operation_name=None):
        if not query:
            return {"errors": [{"message": "Query is empty."}]}

        payload = {
            "query": query,
            "variables": variables or {},
            "operationName": operation_name
        }

        try:
            response = self.session.post(
                self.endpoint,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )

            try:
                res_data = response.json()
                if response.status_code != 200 or "errors" in res_data:
                    logger.error(f"❌ [Qumra Response Error] HTTP {response.status_code}: {res_data}")
                return res_data
            except ValueError:
                logger.error(f"❌ [GraphQL Non-JSON Response] HTTP {response.status_code}: {response.text}")
                return {"errors": [{"message": f"Server returned status {response.status_code}: {response.text}"}]}

        except requests.exceptions.RequestException as e:
            logger.error(f"❌ [GraphQL Network Error]: {str(e)}")
            return {"errors": [{"message": str(e)}]}
