# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة الشامل (مُحدّث بالكامل)

import requests
import logging
from apps.models.orders_db import ProcessedOrder, db
from datetime import datetime

logger = logging.getLogger(__name__)

class SyncEngine:
    API_URL = "https://mahjoub.online/admin/graphql"  
    API_TOKEN = "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"

    @staticmethod
    def _get_headers():
        return {
            "Authorization": f"Bearer {SyncEngine.API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @staticmethod
    def fetch_and_sync_order():
        logger.info("🔄 بدء المزامنة الكاملة مع قمرة...")
        
        # استعلام GraphQL شامل لجلب كافة الحقول الـ 27
        query = """
        query {
            findAllOrders(input: {}) {
                data {
                    _id
                    totalPrice
                    subTotal
                    taxAmount
                    createdAt
                    customer { name phone email }
                    shipping { city district street }
                    status { code }
                    financialStatus
                    items { productTitle sku quantity price }
                }
            }
        }
        """
        
        try:
            response = requests.post(SyncEngine.API_URL, json={'query': query}, headers=SyncEngine._get_headers(), timeout=120)
            result = response.json()
            
            if 'errors' in result:
                logger.error(f"❌ خطأ GraphQL: {result['errors']}")
                return False
            
            orders_data = result.get('data', {}).get('findAllOrders', {}).get('data', [])
            
            for item in orders_data:
                id_api = str(item.get('_id'))
                if not id_api: continue
                    
                order = ProcessedOrder.query.filter_by(id=id_api).first() or ProcessedOrder(id=id_api)
                
                # 1. إسناد البيانات الأساسية
                order.order_id = id_api[-8:] # آخر 8 أرقام
                order.total_price = float(item.get('totalPrice') or 0.0)
                order.sub_total = float(item.get('subTotal') or 0.0)
                order.tax_amount = float(item.get('taxAmount') or 0.0)
                
                # 2. بيانات العميل
                cust = item.get('customer') or {}
                order.customer_name = cust.get('name', 'عميل')
                order.customer_phone = cust.get('phone')
                order.customer_email = cust.get('email')
                
                # 3. بيانات الشحن
                ship = item.get('shipping') or {}
                order.shipping_city = ship.get('city')
                order.shipping_district = ship.get('district')
                order.shipping_street = ship.get('street')
                
                # 4. الحالات
                status_obj = item.get('status') or {}
                order.order_status = status_obj.get('code', 'pending')
                order.financial_status = item.get('financialStatus', 'unpaid')
                order.items_count = len(item.get('items') or [])
                
                db.session.add(order)
            
            db.session.commit()
            logger.info(f"✅ تمت المزامنة بنجاح لـ {len(orders_data)} طلب.")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ فشل المزامنة: {e}")
            return False
