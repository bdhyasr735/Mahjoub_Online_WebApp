# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة المحدث وفقاً لـ Schema النظام

import requests
import logging
from datetime import datetime
from apps.models.orders_db import ProcessedOrder, db
from apps.models.sync_log import SyncLog

logger = logging.getLogger(__name__)

class SyncEngine:
    API_URL = "https://mahjoub.online/admin/graphql"  
    API_TOKEN = "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"

    @staticmethod
    def _get_headers():
        return {
            "Authorization": f"Bearer {SyncEngine.API_TOKEN}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "apollo-require-preflight": "true"
        }

    @staticmethod
    def fetch_and_sync_order():
        logger.info("🔄 بدء عملية مزامنة الطلبات...")
        
        # 🎯 الاستعلام المحدث بناءً على Schema: findAllOrders -> data -> [Order!]
        query = """
        query GetOrders {
            findAllOrders {
                data {
                    id
                    status
                    paymentMethod
                    totalPrice
                    createdAt
                    customer {
                        name
                        phone
                        email
                    }
                    shippingAddress {
                        country
                        city
                        district
                        street
                    }
                }
            }
        }
        """
        
        try:
            response = requests.post(
                SyncEngine.API_URL, 
                json={'query': query}, 
                headers=SyncEngine._get_headers(),
                timeout=120
            )
            
            result = response.json()
            
            if 'errors' in result:
                logger.error(f"❌ خطأ GraphQL: {result['errors']}")
                return False
            
            # 🎯 استخراج الطلبات من المسار الصحيح: findAllOrders -> data
            orders_data = result.get('data', {}).get('findAllOrders', {}).get('data', [])
            
            total_synced = 0
            for item in orders_data:
                id_api = item.get('id')
                if not id_api: continue
                    
                order = ProcessedOrder.query.get(id_api) or ProcessedOrder(id=id_api)
                
                # تحديث الحقول الأساسية
                order.order_status = item.get('status')
                order.payment_type = str(item.get('paymentMethod'))
                order.total_price = float(item.get('totalPrice', 0.0))
                
                # بيانات العميل
                cust = item.get('customer') or {}
                order.customer_name = cust.get('name') or "عميل متجر محجوب"
                order.customer_phone = cust.get('phone', '---')
                order.customer_email = cust.get('email', '---')
                
                # بيانات الشحن
                ship = item.get('shippingAddress') or {}
                order.shipping_country = ship.get('country', 'Yemen')
                order.shipping_city = ship.get('city', '---')
                order.shipping_district = ship.get('district', '---')
                order.shipping_street = ship.get('street', '---')
                
                db.session.add(order)
                total_synced += 1
            
            db.session.commit()
            
            if total_synced > 0:
                log_entry = SyncLog(status="success", message=f"✅ تمت المزامنة بنجاح: {total_synced} طلب.")
                db.session.add(log_entry)
                db.session.commit()
                
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ خطأ أثناء المزامنة: {e}")
            return False

    @staticmethod
    def _execute_mutation(mutation, variables):
        try:
            response = requests.post(
                SyncEngine.API_URL, 
                json={'query': mutation, 'variables': variables}, 
                headers=SyncEngine._get_headers(),
                timeout=120
            )
            return response.json()
        except Exception as e:
            logger.error(f"❌ خطأ في Mutation: {e}")
            return None

    @staticmethod
    def update_order_status(order_id, new_status):
        mutation = """
        mutation updateOrderStatus($id: ID!, $status: String!) {
            updateOrder(input: { id: $id, status: $status }) {
                id
                status
            }
        }
        """
        return SyncEngine._execute_mutation(mutation, {"id": order_id, "status": new_status})

    @staticmethod
    def cancel_order(order_id):
        return SyncEngine.update_order_status(order_id, "cancelled")

    @staticmethod
    def mark_as_fulfilled(order_id):
        return SyncEngine.update_order_status(order_id, "delivered")
