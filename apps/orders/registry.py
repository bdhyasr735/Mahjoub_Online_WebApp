# coding: utf-8
# 📂 apps/orders/services.py

import requests
from apps import db
from apps.models.sync_log import SyncLog
from apps.supplier_wallet.services import WalletService

class OrderService:
    # سيتم استبدال الرابط بـ Endpoint الصحيح الخاص بالمتجر
    API_URL = "https://mahjoub.online/admin/graphql"
    
    @staticmethod
    def get_headers(api_key):
        return {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    @staticmethod
    def fetch_and_sync_orders(api_key, supplier_id):
        """
        جلب الطلبات المكتملة من قمرة ومزامنتها مع محفظة المورد
        """
        # استعلام GraphQL لجلب البيانات المطلوبة فقط
        query = """
        query GetCompletedOrders {
            orders(status: "COMPLETED") {
                id
                netAmount
                currency
            }
        }
        """
        
        try:
            response = requests.post(
                OrderService.API_URL, 
                json={'query': query}, 
                headers=OrderService.get_headers(api_key)
            )
            
            if response.status_code != 200:
                raise Exception(f"خطأ في الاتصال بالـ API: {response.status_code}")

            data = response.json().get('data', {}).get('orders', [])
            
            # معالجة الطلبات واحدة تلو الأخرى
            for order in data:
                # 1. تحديث المحفظة
                WalletService.sync_order_payment(
                    supplier_id=supplier_id,
                    order_id=order['id'],
                    amount=order['netAmount'],
                    currency=order['currency']
                )
            
            # تسجيل نجاح المزامنة
            OrderService.log_sync(supplier_id, 'orders', 'SUCCESS', "تمت المزامنة بنجاح")
            return True

        except Exception as e:
            # تسجيل الفشل في سجل المزامنة (SyncLog)
            OrderService.log_sync(supplier_id, 'orders', 'FAILED', str(e))
            return False

    @staticmethod
    def log_sync(supplier_id, sync_type, status, error_message=None):
        """تسجيل حالة المزامنة في قاعدة البيانات"""
        log = SyncLog(
            supplier_id=supplier_id,
            sync_type=sync_type,
            status=status,
            error_message=error_message
        )
        db.session.add(log)
        db.session.commit()
