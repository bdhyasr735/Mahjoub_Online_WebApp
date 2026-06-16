# 📂 apps/utils/bridge_engine.py
import requests
import logging

logger = logging.getLogger(__name__)

# الرابط الصحيح والمطابق لإعدادات الـ Sandbox الخاصة بك
QUMRA_API_URL = "https://mahjoub.online/admin/graphql" 

def execute_query(query, variables=None):
    """
    المحرك الأساسي لإرسال استعلامات GraphQL إلى الـ Endpoint الصحيح لمتجر محجوب.
    """
    headers = {
        "Content-Type": "application/json",
        # إذا كنت تحتاج إلى مفتاح API أو Token للوصول، يتم تضمينه هنا:
        # "Authorization": "Bearer YOUR_TOKEN_HERE" 
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
