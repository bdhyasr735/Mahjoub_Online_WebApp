# coding: utf-8
# 📂 apps/services/graphql_client.py - النسخة النهائية المتوافقة مع نظام الاستعلامات الخاص

import requests
import logging
from config import Config

logger = logging.getLogger(__name__)

class QomrahGraphQLClient:
    """عميل متخصص لجلب بيانات الطلبات من منصة قمرة عبر محرك الاستعلامات الخاص."""

    @staticmethod
    def _get_headers():
        """تحضير الترويسات الأمنية المطلوبة."""
        return {
            "Authorization": f"Bearer {Config.QUMRA_API_KEY}",
            "Content-Type": "application/json",
            "apollo-require-preflight": "true"
        }

    @staticmethod
    def fetch_orders():
        """جلب بيانات الطلبات باستخدام صيغة QUERY orders."""
        
        # استعلام لجلب آخر الطلبات (يمكنك تعديله حسب حاجتك)
        # هذا الاستعلام يطلب تفاصيل الطلب والحالة بناءً على قائمة الحقول التي حصلنا عليها
        query_string = "QUERY orders METRICS count() AS total_orders, sum(total) AS revenue GROUP BY orderId, status, createdAt SORT createdAt DESC LIMIT 50"
        
        try:
            # نرسل الاستعلام في جسم الطلب (Payload)
            # نستخدم المفتاح 'query' لأن النظام يتوقع نص الاستعلام هنا
            payload = {'query': query_string}
            
            response = requests.post(
                Config.QUMRA_API_URL, 
                json=payload, 
                headers=QomrahGraphQLClient._get_headers(),
                timeout=15
            )
            
            response.raise_for_status()
            # إرجاع البيانات المستلمة
            return response.json()
            
        except requests.exceptions.HTTPError as http_err:
            logger.error(f"❌ خطأ HTTP أثناء الاتصال بـ Qomrah API: {http_err}")
            logger.error(f"Response Content: {response.text}")
            return []
        except Exception as e:
            logger.error(f"❌ خطأ غير متوقع: {e}")
            return []
