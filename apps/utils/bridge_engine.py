# 📂 apps/utils/bridge_engine.py
import requests
import logging

logger = logging.getLogger(__name__)

# الرابط الصحيح والمطابق تماماً لإعدادات الـ Sandbox لنطاقك السيادي
QUMRA_API_URL = "https://mahjoub.online/admin/graphql" 

def execute_query(query, variables=None):
    """
    المحرك الميكروي الأساسي والوحيد لإرسال استعلامات GraphQL حية ومباشرة إلى متجر قمرة.
    """
    headers = {
        "Content-Type": "application/json"
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
            logger.error(f"GraphQL Endpoint Error: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Connection failed to GraphQL Endpoint: {str(e)}")
        return None
