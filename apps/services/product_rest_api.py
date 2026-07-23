# coding: utf-8
# 📂 apps/services/product_rest_api.py

import requests
import os
import json

class ProductRestAPI:
    """التواصل مع قمرة عبر REST API"""
    
    def __init__(self):
        self.api_key = os.environ.get('QUMRA_API_KEY')
        self.base_url = "https://mahjoub.online"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def create_product(self, product_data: dict) -> dict:
        """إنشاء منتج جديد في قمرة عبر REST API"""
        if not self.api_key:
            return {
                'success': False,
                'message': 'QUMRA_API_KEY غير موجود',
                'qid': None
            }
        
        # ✅ تجربة جميع الـ Endpoints الممكنة
        endpoints = [
            f"{self.base_url}/api/products",
            f"{self.base_url}/admin/api/products",
            f"{self.base_url}/products",
            f"{self.base_url}/admin/products",
            f"{self.base_url}/api/v1/products",
            f"{self.base_url}/admin/api/v1/products",
        ]
        
        for url in endpoints:
            try:
                print(f"🔍 محاولة: {url}")
                response = requests.post(
                    url,
                    json=product_data,
                    headers=self.headers,
                    timeout=30
                )
                print(f"   Status: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    qid = data.get('qid') or data.get('data', {}).get('qid')
                    return {
                        'success': True,
                        'qid': qid,
                        'message': 'تم إنشاء المنتج بنجاح'
                    }
            except Exception as e:
                print(f"   ❌ خطأ: {e}")
                continue
        
        return {
            'success': False,
            'message': 'جميع الـ Endpoints فشلت',
            'qid': None
        }
    
    def get_product(self, qid: str) -> dict:
        """جلب منتج من قمرة عبر REST API"""
        endpoints = [
            f"{self.base_url}/api/products/{qid}",
            f"{self.base_url}/admin/api/products/{qid}",
            f"{self.base_url}/products/{qid}",
        ]
        
        for url in endpoints:
            try:
                response = requests.get(url, headers=self.headers, timeout=30)
                if response.status_code == 200:
                    return response.json()
            except:
                continue
        return None
    
    def update_product(self, qid: str, product_data: dict) -> bool:
        """تحديث منتج في قمرة عبر REST API"""
        endpoints = [
            f"{self.base_url}/api/products/{qid}",
            f"{self.base_url}/admin/api/products/{qid}",
            f"{self.base_url}/products/{qid}",
        ]
        
        for url in endpoints:
            try:
                response = requests.put(url, json=product_data, headers=self.headers, timeout=30)
                if response.status_code in [200, 201]:
                    return True
            except:
                continue
        return False
    
    def delete_product(self, qid: str) -> bool:
        """حذف منتج من قمرة عبر REST API"""
        endpoints = [
            f"{self.base_url}/api/products/{qid}",
            f"{self.base_url}/admin/api/products/{qid}",
            f"{self.base_url}/products/{qid}",
        ]
        
        for url in endpoints:
            try:
                response = requests.delete(url, headers=self.headers, timeout=30)
                if response.status_code in [200, 204]:
                    return True
            except:
                continue
        return False


# ✅ للاختبار المباشر
if __name__ == "__main__":
    api = ProductRestAPI()
    
    # ✅ اختبار إنشاء منتج
    test_payload = {
        "title": "منتج تجريبي من REST",
        "price": 99.99,
        "quantity": 5,
        "status": "DRAFT",
        "images": []
    }
    
    print("🔄 جاري اختبار إنشاء منتج...")
    result = api.create_product(test_payload)
    print(f"✅ النتيجة: {result}")
