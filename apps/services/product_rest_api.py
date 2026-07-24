# coding: utf-8
# 📂 apps/services/product_rest_api.py

import requests
import os
import json
import logging
import time
from typing import Dict, List, Optional, Any, Union
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class ProductRestAPI:
    """
    التواصل مع قمرة عبر REST API
    يدعم: المنتجات، الصور، المجموعات، الطلبات
    """
    
    def __init__(self):
        self.api_key = os.environ.get('QUMRA_API_KEY') or os.environ.get('ADMIN_JWT_TOKEN')
        self.base_url = os.environ.get('API_BASE_URL') or "https://mahjoub.online"
        
        # إعداد الجلسة مع إعادة المحاولة
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
        # Headers الأساسية
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Qomrah-Sync-Engine/1.0"
        }
        self.session.headers.update(self.headers)
        
        # قائمة الـ Endpoints للتجربة
        self.endpoints = {
            'upload': [
                "/api/upload",
                "/admin/api/upload",
                "/api/media/upload",
                "/admin/api/media/upload",
                "/api/v1/upload",
                "/admin/api/v1/upload",
            ],
            'products': [
                "/api/products",
                "/admin/api/products",
                "/api/v1/products",
                "/admin/api/v1/products",
                "/products",
                "/admin/products",
            ],
            'collections': [
                "/api/collections",
                "/admin/api/collections",
                "/api/v1/collections",
                "/admin/api/v1/collections",
            ],
            'orders': [
                "/api/orders",
                "/admin/api/orders",
                "/api/v1/orders",
                "/admin/api/v1/orders",
            ],
            'media': [
                "/api/media",
                "/admin/api/media",
                "/api/v1/media",
                "/admin/api/v1/media",
            ]
        }
    
    # ============================================================
    # 🔧 HELPER METHODS - دوال مساعدة
    # ============================================================
    
    def _try_endpoints(self, method: str, endpoints: List[str], 
                       data: Dict = None, params: Dict = None,
                       files: Dict = None, json_data: Dict = None) -> Optional[Dict]:
        """
        محاولة تنفيذ طلب على عدة Endpoints
        
        Args:
            method: طريقة الطلب (GET, POST, PUT, DELETE, PATCH)
            endpoints: قائمة الـ Endpoints
            data: بيانات للـ form-data
            params: معاملات الـ query
            files: ملفات للرفع
            json_data: بيانات JSON
        
        Returns:
            Dict: استجابة الخادم أو None
        """
        for endpoint in endpoints:
            url = f"{self.base_url}{endpoint}"
            try:
                print(f"🔍 محاولة {method} إلى: {url}")
                
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    data=data,
                    json=json_data,
                    files=files,
                    timeout=30
                )
                
                print(f"   📡 Status: {response.status_code}")
                
                if response.status_code in [200, 201, 204]:
                    if response.status_code == 204:
                        return {'success': True, 'data': {}}
                    try:
                        return response.json()
                    except:
                        return {'success': True, 'data': response.text}
                else:
                    print(f"   ❌ فشل: {response.text[:200]}")
                    
            except requests.exceptions.Timeout:
                print(f"   ⏰ Timeout على {endpoint}")
                continue
            except requests.exceptions.ConnectionError:
                print(f"   🔌 Connection Error على {endpoint}")
                continue
            except Exception as e:
                print(f"   ❌ خطأ: {str(e)[:100]}")
                continue
        
        return None
    
    # ============================================================
    # 🖼️ IMAGE UPLOAD - رفع الصور
    # ============================================================
    
    def upload_image(self, image_data: bytes, filename: str,
                    title: str = None, description: str = None) -> Optional[str]:
        """
        رفع صورة إلى مكتبة قمرة
        
        Args:
            image_data: بيانات الصورة (bytes)
            filename: اسم الملف
            title: عنوان الصورة (اختياري)
            description: وصف الصورة (اختياري)
        
        Returns:
            str: رابط الصورة في قمرة أو None
        """
        if not self.api_key:
            print("❌ QUMRA_API_KEY غير موجود")
            return None
        
        # تحديد نوع الصورة
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
        
        # إعداد الملفات
        files = {
            'file': (filename, image_data, f'image/{ext}')
        }
        if title:
            files['title'] = (None, title)
        if description:
            files['description'] = (None, description)
        
        result = self._try_endpoints(
            method='POST',
            endpoints=self.endpoints['upload'],
            files=files
        )
        
        if result:
            # استخراج رابط الصورة من الاستجابة
            image_url = (
                result.get('url') or
                result.get('fileUrl') or
                result.get('data', {}).get('fileUrl') or
                result.get('data', {}).get('url') or
                result.get('image', {}).get('url')
            )
            if image_url:
                print(f"✅ تم رفع الصورة بنجاح: {image_url}")
                return image_url
            else:
                print(f"⚠️ استجابة بدون رابط: {result}")
                return None
        
        print("❌ فشل رفع الصورة في جميع الـ Endpoints")
        return None
    
    def upload_multiple_images(self, images: List[Dict]) -> List[str]:
        """
        رفع صور متعددة
        
        Args:
            images: قائمة من {"data": bytes, "filename": str, "title": str}
        
        Returns:
            List[str]: قائمة روابط الصور المرفوعة
        """
        uploaded_urls = []
        for img in images:
            url = self.upload_image(
                img['data'],
                img['filename'],
                img.get('title'),
                img.get('description')
            )
            if url:
                uploaded_urls.append(url)
        return uploaded_urls
    
    # ============================================================
    # 📦 PRODUCT OPERATIONS - عمليات المنتجات
    # ============================================================
    
    def create_product(self, product_data: Dict) -> Dict:
        """
        إنشاء منتج جديد في قمرة عبر REST API
        
        Args:
            product_data: بيانات المنتج {
                'title': str,
                'description': str,
                'price': float,
                'quantity': int,
                'images': List[str],
                'status': str (DRAFT, PUBLISHED, ACTIVE, INACTIVE)
            }
        
        Returns:
            Dict: {'success': bool, 'qid': str, 'message': str, 'data': dict}
        """
        if not self.api_key:
            return {
                'success': False,
                'message': 'QUMRA_API_KEY غير موجود',
                'qid': None,
                'data': None
            }
        
        # بناء البيانات
        payload = {
            "title": product_data.get('title', ''),
            "description": product_data.get('description', ''),
            "price": float(product_data.get('price', 0)),
            "quantity": int(product_data.get('quantity', 0)),
            "status": product_data.get('status', 'DRAFT'),
            "images": product_data.get('images', [])
        }
        
        # إضافة حقول إضافية إن وجدت
        if 'sku' in product_data:
            payload['sku'] = product_data['sku']
        if 'weight' in product_data:
            payload['weight'] = product_data['weight']
        if 'dimensions' in product_data:
            payload['dimensions'] = product_data['dimensions']
        if 'tags' in product_data:
            payload['tags'] = product_data['tags']
        if 'collections' in product_data:
            payload['collections'] = product_data['collections']
        
        result = self._try_endpoints(
            method='POST',
            endpoints=self.endpoints['products'],
            json_data=payload
        )
        
        if result:
            # استخراج الـ QID من الاستجابة
            qid = (
                result.get('qid') or
                result.get('data', {}).get('qid') or
                result.get('product', {}).get('qid') or
                result.get('_id')
            )
            
            return {
                'success': True,
                'qid': qid,
                'message': 'تم إنشاء المنتج بنجاح',
                'data': result.get('data', result)
            }
        
        return {
            'success': False,
            'message': 'فشل إنشاء المنتج',
            'qid': None,
            'data': None
        }
    
    def get_product(self, qid: str) -> Optional[Dict]:
        """
        جلب منتج من قمرة عبر REST API
        
        Args:
            qid: معرف المنتج
        
        Returns:
            Dict: بيانات المنتج أو None
        """
        endpoints = [f"{endpoint}/{qid}" for endpoint in self.endpoints['products']]
        result = self._try_endpoints('GET', endpoints)
        return result
    
    def get_all_products(self, page: int = 1, limit: int = 50,
                        status: str = None, search: str = None) -> List[Dict]:
        """
        جلب جميع المنتجات مع فلترة
        
        Args:
            page: رقم الصفحة
            limit: عدد المنتجات في الصفحة
            status: فلترة حسب الحالة
            search: نص البحث
        
        Returns:
            List[Dict]: قائمة المنتجات
        """
        params = {'page': page, 'limit': limit}
        if status:
            params['status'] = status
        if search:
            params['search'] = search
        
        result = self._try_endpoints('GET', self.endpoints['products'], params=params)
        
        if result:
            products = (
                result.get('data', []) or
                result.get('products', []) or
                result.get('items', [])
            )
            return products
        return []
    
    def update_product(self, qid: str, product_data: Dict) -> bool:
        """
        تحديث منتج في قمرة عبر REST API
        
        Args:
            qid: معرف المنتج
            product_data: بيانات التحديث
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        endpoints = [f"{endpoint}/{qid}" for endpoint in self.endpoints['products']]
        result = self._try_endpoints('PUT', endpoints, json_data=product_data)
        return result is not None
    
    def patch_product(self, qid: str, product_data: Dict) -> bool:
        """
        تحديث جزئي لمنتج (PATCH)
        
        Args:
            qid: معرف المنتج
            product_data: بيانات التحديث الجزئي
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        endpoints = [f"{endpoint}/{qid}" for endpoint in self.endpoints['products']]
        result = self._try_endpoints('PATCH', endpoints, json_data=product_data)
        return result is not None
    
    def delete_product(self, qid: str) -> bool:
        """
        حذف منتج من قمرة عبر REST API
        
        Args:
            qid: معرف المنتج
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        endpoints = [f"{endpoint}/{qid}" for endpoint in self.endpoints['products']]
        result = self._try_endpoints('DELETE', endpoints)
        return result is not None
    
    def bulk_delete_products(self, qids: List[str]) -> bool:
        """
        حذف منتجات متعددة
        
        Args:
            qids: قائمة معرفات المنتجات
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        endpoints = [f"{endpoint}/bulk" for endpoint in self.endpoints['products']]
        result = self._try_endpoints('DELETE', endpoints, json_data={'qids': qids})
        return result is not None
    
    # ============================================================
    # 📂 COLLECTION OPERATIONS - عمليات المجموعات
    # ============================================================
    
    def create_collection(self, collection_data: Dict) -> Dict:
        """
        إنشاء مجموعة جديدة
        
        Args:
            collection_data: بيانات المجموعة {
                'title': str,
                'description': str,
                'image': str (url)
            }
        
        Returns:
            Dict: {'success': bool, 'qid': str, 'message': str}
        """
        if not self.api_key:
            return {'success': False, 'message': 'QUMRA_API_KEY غير موجود', 'qid': None}
        
        result = self._try_endpoints(
            method='POST',
            endpoints=self.endpoints['collections'],
            json_data=collection_data
        )
        
        if result:
            qid = result.get('qid') or result.get('data', {}).get('qid')
            return {
                'success': True,
                'qid': qid,
                'message': 'تم إنشاء المجموعة بنجاح',
                'data': result
            }
        
        return {'success': False, 'message': 'فشل إنشاء المجموعة', 'qid': None}
    
    def get_all_collections(self, page: int = 1, limit: int = 50) -> List[Dict]:
        """
        جلب جميع المجموعات
        
        Args:
            page: رقم الصفحة
            limit: عدد المجموعات في الصفحة
        
        Returns:
            List[Dict]: قائمة المجموعات
        """
        params = {'page': page, 'limit': limit}
        result = self._try_endpoints('GET', self.endpoints['collections'], params=params)
        
        if result:
            collections = result.get('data', []) or result.get('collections', [])
            return collections
        return []
    
    def delete_collection(self, qid: str) -> bool:
        """
        حذف مجموعة
        
        Args:
            qid: معرف المجموعة
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        endpoints = [f"{endpoint}/{qid}" for endpoint in self.endpoints['collections']]
        result = self._try_endpoints('DELETE', endpoints)
        return result is not None
    
    # ============================================================
    # 📦 ORDER OPERATIONS - عمليات الطلبات
    # ============================================================
    
    def get_all_orders(self, page: int = 1, limit: int = 50,
                      status: str = None) -> List[Dict]:
        """
        جلب جميع الطلبات
        
        Args:
            page: رقم الصفحة
            limit: عدد الطلبات في الصفحة
            status: فلترة حسب الحالة
        
        Returns:
            List[Dict]: قائمة الطلبات
        """
        params = {'page': page, 'limit': limit}
        if status:
            params['status'] = status
        
        result = self._try_endpoints('GET', self.endpoints['orders'], params=params)
        
        if result:
            orders = result.get('data', []) or result.get('orders', [])
            return orders
        return []
    
    def get_order_by_id(self, order_id: str) -> Optional[Dict]:
        """
        جلب طلب بواسطة معرفه
        
        Args:
            order_id: معرف الطلب
        
        Returns:
            Dict: بيانات الطلب
        """
        endpoints = [f"{endpoint}/{order_id}" for endpoint in self.endpoints['orders']]
        return self._try_endpoints('GET', endpoints)
    
    def update_order_status(self, order_id: str, status: str) -> bool:
        """
        تحديث حالة الطلب
        
        Args:
            order_id: معرف الطلب
            status: الحالة الجديدة
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        endpoints = [f"{endpoint}/{order_id}/status" for endpoint in self.endpoints['orders']]
        result = self._try_endpoints('PUT', endpoints, json_data={'status': status})
        return result is not None
    
    # ============================================================
    # 📋 MEDIA OPERATIONS - عمليات الوسائط
    # ============================================================
    
    def get_all_media(self, page: int = 1, limit: int = 50) -> List[Dict]:
        """
        جلب جميع الوسائط
        
        Args:
            page: رقم الصفحة
            limit: عدد الوسائط في الصفحة
        
        Returns:
            List[Dict]: قائمة الوسائط
        """
        params = {'page': page, 'limit': limit}
        result = self._try_endpoints('GET', self.endpoints['media'], params=params)
        
        if result:
            media = result.get('data', []) or result.get('media', [])
            return media
        return []
    
    def delete_media(self, media_id: str) -> bool:
        """
        حذف وسيط
        
        Args:
            media_id: معرف الوسيط
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        endpoints = [f"{endpoint}/{media_id}" for endpoint in self.endpoints['media']]
        result = self._try_endpoints('DELETE', endpoints)
        return result is not None
    
    # ============================================================
    # 📊 STATISTICS - إحصائيات
    # ============================================================
    
    def get_stats(self) -> Dict:
        """
        الحصول على إحصائيات عامة
        
        Returns:
            Dict: {products: int, orders: int, collections: int, media: int}
        """
        stats = {
            'products': 0,
            'orders': 0,
            'collections': 0,
            'media': 0
        }
        
        # جلب إحصائيات المنتجات
        products = self.get_all_products(page=1, limit=1)
        if isinstance(products, dict) and 'total' in products:
            stats['products'] = products['total']
        elif isinstance(products, list):
            stats['products'] = len(products)
        
        # جلب إحصائيات المجموعات
        collections = self.get_all_collections(page=1, limit=1)
        if isinstance(collections, dict) and 'total' in collections:
            stats['collections'] = collections['total']
        elif isinstance(collections, list):
            stats['collections'] = len(collections)
        
        # جلب إحصائيات الطلبات
        orders = self.get_all_orders(page=1, limit=1)
        if isinstance(orders, dict) and 'total' in orders:
            stats['orders'] = orders['total']
        elif isinstance(orders, list):
            stats['orders'] = len(orders)
        
        # جلب إحصائيات الوسائط
        media = self.get_all_media(page=1, limit=1)
        if isinstance(media, dict) and 'total' in media:
            stats['media'] = media['total']
        elif isinstance(media, list):
            stats['media'] = len(media)
        
        return stats
    
    # ============================================================
    # 🔄 SYNC OPERATIONS - عمليات المزامنة
    # ============================================================
    
    def sync_product(self, qid: str, product_data: Dict) -> Dict:
        """
        مزامنة كاملة للمنتج (إنشاء أو تحديث)
        
        Args:
            qid: معرف المنتج (إذا كان موجوداً)
            product_data: بيانات المنتج
        
        Returns:
            Dict: {'action': 'created'|'updated'|'failed', 'qid': str, 'message': str}
        """
        # التحقق إذا كان المنتج موجوداً
        existing = self.get_product(qid) if qid else None
        
        if existing:
            # تحديث المنتج
            success = self.update_product(qid, product_data)
            return {
                'action': 'updated',
                'qid': qid,
                'message': 'تم تحديث المنتج بنجاح' if success else 'فشل تحديث المنتج'
            }
        else:
            # إنشاء منتج جديد
            result = self.create_product(product_data)
            return {
                'action': 'created',
                'qid': result.get('qid'),
                'message': result.get('message', 'تم إنشاء المنتج بنجاح' if result.get('success') else 'فشل إنشاء المنتج')
            }


# ============================================================
# 🚀 SINGLETON INSTANCE
# ============================================================

product_rest = ProductRestAPI()


# ============================================================
# 📋 EXPORTS - للاستخدام المباشر
# ============================================================

__all__ = [
    'ProductRestAPI',
    'product_rest'
]


# ============================================================
# 🧪 TEST - اختبار سريع
# ============================================================

if __name__ == "__main__":
    api = ProductRestAPI()
    
    print("🔄 جاري اختبار الاتصال...")
    
    # ✅ اختبار جلب المنتجات
    try:
        products = api.get_all_products(limit=5)
        print(f"✅ تم جلب {len(products)} منتج")
    except Exception as e:
        print(f"❌ خطأ في جلب المنتجات: {e}")
    
    # ✅ اختبار الإحصائيات
    try:
        stats = api.get_stats()
        print(f"📊 الإحصائيات: {stats}")
    except Exception as e:
        print(f"❌ خطأ في الإحصائيات: {e}")
    
    # ✅ اختبار إنشاء منتج
    test_payload = {
        "title": "منتج تجريبي من REST API",
        "price": 99.99,
        "quantity": 10,
        "status": "DRAFT",
        "description": "منتج تجريبي للاختبار"
    }
    
    print("\n🔄 جاري اختبار إنشاء منتج...")
    result = api.create_product(test_payload)
    print(f"✅ النتيجة: {result}")
