# coding: utf-8
# 📂 apps/utils/bridge_engine.py

import requests
import os
import logging

logger = logging.getLogger(__name__)

class QumraBridgeEngine:
    def __init__(self):
        self.endpoint = "https://mahjoub.online/admin/graphql"
        # التأكد من جلب المفتاح من متغيرات البيئة
        api_token = os.environ.get('QUMRA_API_KEY', '').strip()
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def execute_query(self, query, variables=None):
        """دالة موحدة لتنفيذ أي استعلام GraphQL"""
        payload = {"query": query, "variables": variables or {}}
        try:
            response = requests.post(self.endpoint, json=payload, headers=self.headers, timeout=15)
            return response.json()
        except Exception as e:
            logger.error(f"⚠️ Connection Error: {e}")
            return {}

    def fetch_latest_products(self):
        """جلب المنتجات (تعمل حالياً لديك)"""
        query = """
        query {
            findAllProducts {
                data {
                    title
                    pricing { price }
                    quantity
                    status
                    images { fileUrl }
                }
            }
        }
        """
        result = self.execute_query(query)
        products = result.get('data', {}).get('findAllProducts', {}).get('data', [])
        
        processed_products = []
        for p in products:
            pricing = p.get('pricing') or {}
            images = p.get('images') or []
            
            img_url = images[0].get('fileUrl') if images else None
            
            processed_products.append({
                'title': p.get('title'),
                'price': pricing.get('price', 0),
                'quantity': p.get('quantity', 0),
                'status': p.get('status'),
                'image_url': img_url
            })
        return processed_products

    def fetch_latest_orders(self):
        """جلب الطلبات - تحتاج تأكد من تفعيل صلاحية orders:read في قمرة"""
        query = """
        query {
            findAllOrders(input: { limit: 20, page: 1 }) {
                data {
                    _id
                    totalPrice
                    status { name }
                    account { name }
                }
            }
        }
        """
        result = self.execute_query(query)
        
        # تسجيل الأخطاء إذا وجدت (مفيد للـ Debugging في Render)
        if 'errors' in result:
            logger.error(f"⚠️ GraphQL Errors: {result['errors']}")
            return []
            
        return result.get('data', {}).get('findAllOrders', {}).get('data', [])
