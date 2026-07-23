# coding: utf-8
# 📂 apps/services/product_rest_api.py

import requests
import os
import json

class ProductRestAPI:
    """التواصل مع قمرة عبر REST API"""
    
    def __init__(self):
        self.api_key = os.environ.get('QUMRA_API_KEY')
        self.base_url = "https://mahjoub.online/api"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def create_product(self, product_data: dict) -> dict:
        """
        إنشاء منتج جديد في قمرة عبر REST API
        
        Args:
            product_data: بيانات المنتج {
                'title': str,
                'description': str,
                'price': float,
                'quantity': int,
                'images': list,
                'status': str (DRAFT, PUBLISHED)
            }
        
        Returns:
            dict: {'success': bool, 'qid': str, 'message': str}
        """
        if not self.api_key:
            return {
                'success': False,
                'message': 'QUMRA_API_KEY غير موجود',
                'qid': None
            }
        
        url = f"{self.base_url}/products"
        
        payload = {
            "title": product_data.get('title', ''),
            "description": product_data.get('description', ''),
            "price": float(product_data.get('price', 0)),
            "quantity": int(product_data.get('quantity', 0)),
            "status": product_data.get('status', 'DRAFT'),
            "images": product_data.get('images', [])
        }
        
        try:
            response = requests.post(
                url,
                json=payload,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                data = response.json()
                qid = data.get('qid') or data.get('data', {}).get('qid')
                return {
                    'success': True,
                    'qid': qid,
                    'message': 'تم إنشاء المنتج بنجاح'
                }
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'message': f'HTTP Error {response.status_code}',
                    'qid': None
                }
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request Error: {e}")
            return {
                'success': False,
                'message': str(e),
                'qid': None
            }
        except Exception as e:
            print(f"❌ خطأ في create_product: {e}")
            return {
                'success': False,
                'message': str(e),
                'qid': None
            }
    
    def get_product(self, qid: str) -> dict:
        """جلب منتج من قمرة عبر REST API"""
        url = f"{self.base_url}/products/{qid}"
        
        try:
            response = requests.get(
                url,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ خطأ في get_product: {e}")
            return None
    
    def update_product(self, qid: str, product_data: dict) -> bool:
        """تحديث منتج في قمرة عبر REST API"""
        url = f"{self.base_url}/products/{qid}"
        
        try:
            response = requests.put(
                url,
                json=product_data,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code in [200, 201]:
                return True
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في update_product: {e}")
            return False
    
    def delete_product(self, qid: str) -> bool:
        """حذف منتج من قمرة عبر REST API"""
        url = f"{self.base_url}/products/{qid}"
        
        try:
            response = requests.delete(
                url,
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code in [200, 204]:
                return True
            else:
                print(f"❌ HTTP Error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ خطأ في delete_product: {e}")
            return False
