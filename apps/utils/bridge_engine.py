# 📂 apps/utils/bridge_engine.py
import requests
import time
from config import Config

_CACHE = {"products": [], "last_updated": 0}
CACHE_TIMEOUT = 3600 

class QumraBridgeEngine:
    def __init__(self):
        self.endpoint = Config.QUMRA_API_URL
        self.headers = {
            "Authorization": f"Bearer {Config.QUMRA_API_KEY}",
            "Content-Type": "application/json"
        }

    def sync_all_data(self):
        # يتم استدعاء هذا فقط عند الضغط على زر المزامنة
        try:
            query = "{ findAllProducts { data { title pricing { price } quantity images { fileUrl } } } }"
            response = requests.post(self.endpoint, json={"query": query}, headers=self.headers, timeout=10)
            if response.status_code == 200:
                data = response.json().get('data', {}).get('findAllProducts', {}).get('data', [])
                _CACHE["products"] = data
                _CACHE["last_updated"] = time.time()
                return True
        except: return False
        return False

    def get_data(self, search=""):
        # خفيف جداً: فلترة محلية من الذاكرة
        products = _CACHE["products"]
        if search:
            products = [p for p in products if search.lower() in p['title'].lower()]
        return products
