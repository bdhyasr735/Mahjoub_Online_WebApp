import requests
import os

# جلب الإعدادات من متغيرات البيئة التي رأيناها في Railway
QUMRA_API_URL = os.getenv("QUMRA_API_URL")  # https://mahjoub.online/admin/graphql
QUMRA_API_KEY = os.getenv("QUMRA_API_KEY")  # qmr_79e068ae...

def query_qumra(query, variables=None):
    """
    الدالة السيادية لإرسال استعلامات GraphQL إلى قمرة
    """
    headers = {
        "Authorization": f"Bearer {QUMRA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"query": query, "variables": variables}
    
    try:
        response = requests.post(QUMRA_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"🔴 خطأ في الاتصال بـ Qumra GraphQL: {e}")
        return None

def fetch_collections_from_qumra():
    """
    جلب الأقسام (Collections) لعرضها في قائمة اختيار المورد
    """
    # استعلام GraphQL لجلب المعرف والاسم لكل قسم
    query = """
    query {
      collections(first: 50) {
        edges {
          node {
            id
            name
          }
        }
      }
    }
    """
    result = query_qumra(query)
    if result and 'data' in result:
        # تبسيط البيانات لتكون قائمة (ID, Name)
        return [
            (edge['node']['id'], edge['node']['name']) 
            for edge in result['data']['collections']['edges']
        ]
    return []
