# 📂 apps/utils/bridge_engine.py
import requests
import logging

logger = logging.getLogger(__name__)

# الرابط الفعلي والمباشر لنظامك بناءً على إعدادات الـ Sandbox الخاصة بك
QUMRA_API_URL = "https://mahjoub.online/admin/graphql" 

def execute_query(query, variables=None):
    """
    المحرك الأساسي لإرسال استعلامات GraphQL إلى الـ Endpoint الصحيح لمتجر محجوب.
    """
    headers = {
        "Content-Type": "application/json",
        # يمكنك إضافة الـ Authorization Token هنا إذا كان نظام قمرة يتطلبه خارج الـ Sandbox
        # "Authorization": "Bearer YOUR_ACCESS_TOKEN"
    }
    
    payload = {
        "query": query,
        "variables": variables or {}
    }
    
    try:
        response = requests.post(QUMRA_API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Qumra API Error: Status {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Connection failed to Qumra API: {str(e)}")
        return None
