# 📂 apps/utils/bridge_engine.py
import requests
import logging

logger = logging.getLogger(__name__)

# الرابط السيادي Sandbox المباشر والصحيح والمطابق تماماً لإعدادات الـ Sandbox
QUMRA_API_URL = "https://mahjoub.online/admin/graphql"

def execute_query(query, variables=None):
    """المحرك الأساسي والوحيد لإرسال استعلامات GraphQL"""
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
