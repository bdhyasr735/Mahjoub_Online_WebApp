# coding: utf-8
# 📂 apps/orders/services.py

import requests
from apps.extensions import db
from apps.models.sync_log import SyncLog
from apps.models.orders_db import Order
from apps.models.financials_db import OrderFinancial
from apps.supplier_wallet.services import WalletService

class OrderService:
    # الرابط ثابت، بينما المفتاح سيتم جلبه من البيئة (Environment Variable)
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
        جلب الطلبات من API قمرة ومزامنتها مع النظام الداخلي والمحفظة.
        """
        # استعلام GraphQL المحدث ليشمل كافة الحقول المطلوبة
        query = """
        query GetCompletedOrders {
            orders(status: "COMPLETED") {
                orderId
                customerName
                status
                total
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
            
            # معالجة الطلبات
            for order_data in data:
                # 1. التحقق من عدم تكرار الطلب
                if not Order.query.filter_by(id=order_data['orderId']).first():
                    
                    # 2. إنشاء الطلب في قاعدة البيانات
                    new_order = Order(
                        id=order_data['orderId'],
                        customer_name=order_data.get('customerName', 'عميل'),
                        status=order_data.get('status', 'completed')
                    )
                    db.session.add(new_order)
                    
                    # 3. إنشاء السجل المالي
                    new_financial = OrderFinancial(
                        order_id=new_order.id,
                        supplier_id=supplier_id,
                        total_paid=order_data['total'],
                        supplier_cost=0, 
                        mahjoub_commission=order_data['total'],
                        settlement_status='pending'
                    )
                    db.session.add(new_financial)
                
                # 4. تحديث المحفظة (الارتباط المالي)
                WalletService.sync_order_payment(
                    supplier_id=supplier_id,
                    order_id=order_data['orderId'],
                    amount=order_data['total'],
                    currency=order_data['currency']
                )
            
            # حفظ كافة التغييرات
            db.session.commit()
            OrderService.log_sync(supplier_id, 'orders', 'SUCCESS', "تمت المزامنة بنجاح وجلب كافة البيانات")
            return True

        except Exception as e:
            db.session.rollback()
            OrderService.log_sync(supplier_id, 'orders', 'FAILED', str(e))
            return False

    @staticmethod
    def log_sync(supplier_id, sync_type, status, error_message=None):
        """تسجيل حالة العملية في قاعدة البيانات"""
        log = SyncLog(
            supplier_id=supplier_id,
            sync_type=sync_type,
            status=status,
            error_message=str(error_message)
        )
        db.session.add(log)
        db.session.commit()
