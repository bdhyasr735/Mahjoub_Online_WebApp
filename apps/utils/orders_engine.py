# 📂 apps/utils/bridge_engine.py
import requests
import logging

logger = logging.getLogger(__name__)

# ضع رابط الـ API الخاص بـ قمرة هنا (أو اتركه يقرأ من متغيرات البيئة)
QUMRA_API_URL = "https://api.qumra.sa/graphql" 

def execute_query(query, variables=None):
    """
    المحرك الأساسي لإرسال استعلامات GraphQL إلى منصة قمرة.
    """
    headers = {
        "Content-Type": "application/json",
        # "Authorization": "Bearer YOUR_TOKEN_HERE" # أضف التوكن الخاص بك هنا إذا كان مطلوباً
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
