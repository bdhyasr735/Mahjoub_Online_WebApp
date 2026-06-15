# 📂 apps/utils/bridge_engine.py
import requests
from config import Config
import logging

logger = logging.getLogger(__name__)

class QumraBridgeEngine:
    def __init__(self):
        self.endpoint = Config.QUMRA_API_URL
        self.headers = {
            "Authorization": f"Bearer {Config.QUMRA_API_KEY}",
            "Content-Type": "application/json"
        }

    def execute_query(self, query):
        """دالة مركزية لتنفيذ أي استعلام GraphQL"""
        try:
            response = requests.post(
                self.endpoint, 
                json={"query": query}, 
                headers=self.headers, 
                timeout=15
            )
            logger.info(f"API_RESPONSE: {response.text}")
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            logger.error(f"Connection Error: {str(e)}")
            return None
