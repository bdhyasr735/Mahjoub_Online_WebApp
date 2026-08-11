# coding: utf-8
# 📂 apps/services/graphql_client.py

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

        # تحويل الاستجابة إلى JSON لقراءة تفاصيل الخطأ المباشرة من Qumra
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
