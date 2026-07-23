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
    
    # ============================================================
    # ✅ رفع صورة إلى مكتبة قمرة
    # ============================================================
    def upload_image(self, image_data: bytes, filename: str) -> str:
        """
        رفع صورة إلى مكتبة قمرة
        
        Args:
            image_data: بيانات الصورة (bytes)
            filename: اسم الملف
        
        Returns:
            str: رابط الصورة في قمرة
        """
        if not self.api_key:
            print("❌ QUMRA_API_KEY غير موجود")
            return None
        
        # ✅ جرب عدة Endpoints للرفع
        endpoints = [
            f"{self.base_url}/api/upload",
            f"{self.base_url}/admin/api/upload",
            f"{self.base_url}/api/media",
            f"{self.base_url}/admin/api/media",
            f"{self.base_url}/api/images",
            f"{self.base_url}/admin/api/images",
            f"{self.base_url}/upload",
            f"{self.base_url}/admin/upload",
        ]
        
        files = {
            'file': (filename, image_data, 'image/jpeg')
        }
        
        for url in endpoints:
            try:
                print(f"🔍 محاولة رفع الصورة إلى: {url}")
                response = requests.post(
                    url,
                    files=files,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    timeout=30
                )
                print(f"   Status: {response.status_code}")
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    # ✅ استخراج رابط الصورة من الاستجابة
                    image_url = (
                        data.get('url') or 
                        data.get('fileUrl') or 
                        data.get('data', {}).get('fileUrl') or
                        data.get('data', {}).get('url')
                    )
                    if image_url:
                        print(f"✅ تم رفع الصورة بنجاح: {image_url}")
                        return image_url
                    else:
                        print(f"⚠️ استجابة بدون رابط: {data}")
                else:
                    print(f"   ❌ فشل: {response.text[:100]}")
            except Exception as e:
                print(f"   ❌ خطأ: {e}")
                continue
        
        print("❌ فشل رفع الصورة في جميع الـ Endpoints")
        return None
    
    # ============================================================
    # ✅ إنشاء منتج
    # ============================================================
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
        
        # ✅ جرب عدة Endpoints للإنشاء
        endpoints = [
            f"{self.base_url}/api/products",
            f"{self.base_url}/admin/api/products",
            f"{self.base_url}/products",
            f"{self.base_url}/admin/products",
            f"{self.base_url}/api/v1/products",
            f"{self.base_url}/admin/api/v1/products",
        ]
        
        payload = {
            "title": product_data.get('title', ''),
            "description": product_data.get('description', ''),
            "price": float(product_data.get('price', 0)),
            "quantity": int(product_data.get('quantity', 0)),
            "status": product_data.get('status', 'DRAFT'),
            "images": product_data.get('images', [])
        }
        
        for url in endpoints:
            try:
                print(f"🔍 محاولة إنشاء منتج إلى: {url}")
                response = requests.post(
                    url,
                    json=payload,
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
                else:
                    print(f"   ❌ فشل: {response.text[:100]}")
            except Exception as e:
                print(f"   ❌ خطأ: {e}")
                continue
        
        return {
            'success': False,
            'message': 'جميع الـ Endpoints فشلت في إنشاء المنتج',
            'qid': None
        }
    
    # ============================================================
    # ✅ جلب منتج
    # ============================================================
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
    
    # ============================================================
    # ✅ تحديث منتج
    # ============================================================
    def update_product(self, qid: str, product_data: dict) -> bool:
        """تحديث منتج في قمرة عبر REST API"""
        endpoints = [
            f"{self.base_url}/api/products/{qid}",
            f"{self.base_url}/admin/api/products/{qid}",
            f"{self.base_url}/products/{qid}",
        ]
        
        for url in endpoints:
            try:
                response = requests.put(
                    url,
                    json=product_data,
                    headers=self.headers,
                    timeout=30
                )
                if response.status_code in [200, 201]:
                    return True
            except:
                continue
        return False
    
    # ============================================================
    # ✅ حذف منتج
    # ============================================================
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
    
    # ✅ اختبار رفع صورة (إذا كان لديك صورة)
    # with open("test.jpg", "rb") as f:
    #     image_data = f.read()
    #     url = api.upload_image(image_data, "test.jpg")
    #     print(f"رابط الصورة: {url}")
    
    # ✅ اختبار إنشاء منتج
    test_payload = {
        "title": "منتج تجريبي من REST API",
        "price": 99.99,
        "quantity": 10,
        "status": "DRAFT",
        "images": [],
        "description": "منتج تجريبي للاختبار"
    }
    
    print("\n🔄 جاري اختبار إنشاء منتج...")
    result = api.create_product(test_payload)
    print(f"✅ النتيجة: {result}")
