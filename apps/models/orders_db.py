# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة السيادي والربط التكاملي مع قمرة كلاود (النسخة التصحيحية النهائية)

import requests
import logging
from datetime import datetime
from apps.extensions import db
from apps.models.orders_db import ProcessedOrder, OrderItem
from config import Config

logger = logging.getLogger(__name__)

class SyncEngine:
    """المحرك المركزي لإدارة وضبط عمليات المزامنة والتحديث الفوري للطلبات والحالات مع سيرفر قمرة"""

    @staticmethod
    def get_headers():
        """توليد ترويسة الطلب الأمنية باستخدام رمز الوصول السيادي المحدث"""
        token = getattr(Config, 'QOMRAH_ACCESS_TOKEN', '')
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    @staticmethod
    def fetch_and_sync_order():
        """جلب ومزامنة كافة الطلبات من قمرة ومعالجتها فورياً داخل قاعدة البيانات المحلية"""
        url = "https://api.qomrah.cloud/graphql" # مسار بوابة الـ GraphQL الموحدة لقمرة
        
        # 🎯 الاستعلام المصحح والمطابق تماماً لقيود التحقق في السيرفر (GraphQL Validation Matches)
        query = """
        query findAllOrders($page: Int) {
            orders(page: $page) {
                id
                status
                paymentMethod
                total
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
        """
        
        variables = {"page": 1}
        payload = {"query": query, "variables": variables}
        
        try:
            response = requests.post(url, json=payload, headers=SyncEngine.get_headers(), timeout=15)
            response_json = response.json()
            
            # التحقق من وجود أخطاء صريحة صادرة من التحقق الداخلي للسيرفر
            if 'errors' in response_json:
                logger.error(f"❌ خطأ تدوين من سيرفر قمرة: {response_json['errors']}")
                return False
                
            orders_data = response_json.get('data', {}).get('orders', [])
            if not orders_data:
                logger.info("ℹ️ لم يتم العثور على أي طلبات جديدة بانتظار المزامنة.")
                return True

            for order_node in orders_data:
                order_id_raw = order_node.get('id')
                if not order_id_raw:
                    continue
                    
                # البحث عن الطلب محلياً لتحديثه أو إنشاء طلب جديد (Upsert)
                order = ProcessedOrder.query.get(order_id_raw)
                if not order:
                    order = ProcessedOrder(id=order_id_raw)
                    db.session.add(order)
                
                # 🧭 خريطة تحويل وتوزيع البيانات (Data Mapping) إلى النموذج المحلي
                order.order_id = order_id_raw.split('-')[-1] if '-' in order_id_raw else order_id_raw  # رقم افتراضي مشتق أو رقم الهوية
                order.order_status = order_node.get('status', 'pending')
                order.payment_type = order_node.get('paymentMethod', 'manual')
                
                # إسناد السعر الإجمالي (يتم تشفيره بـ AES-256 تلقائياً عبر الـ Setter في الموديل)
                order.total_price = order_node.get('total', 0.0)
                
                # معالجة تفكيك كائن بيانات العميل المتداخل (Nested Customer Object)
                customer_data = order_node.get('customer') or {}
                order.customer_name = customer_data.get('name', '---')
                order.customer_phone = customer_data.get('phone', '---')
                order.customer_email = customer_data.get('email', '---')
                
                # معالجة تفكيك كائن العنوان الجغرافي (Nested Shipping Object)
                shipping_data = order_node.get('shippingAddress') or {}
                order.shipping_country = shipping_data.get('country', 'Yemen')
                order.shipping_city = shipping_data.get('city', '---')
                order.shipping_district = shipping_data.get('district', '---')
                order.shipping_street = shipping_data.get('street', '---')
                
                # معالجة تاريخ الإنشاء بأمان
                created_at_str = order_node.get('createdAt')
                if created_at_str:
                    try:
                        order.created_at_api = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                    except Exception:
                        order.created_at_api = datetime.utcnow()
                else:
                    order.created_at_api = datetime.utcnow()
                    
            db.session.commit()
            logger.info("✅ تمت المزامنة الشاملة وحفظ البيانات في قاعدة البيانات بنجاح.")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ انهيار محرك المزامنة أثناء الاتصال الخارجي: {e}")
            return False

    @staticmethod
    def update_order_status(order_id, new_status):
        """تحديث حالة الطلب وإرسال التعديل الفوري عبر الـ Mutation إلى سيرفر قمرة"""
        url = "https://api.qomrah.cloud/graphql"
        mutation = """
        mutation updateOrderStatus($id: ID!, $status: String!) {
            updateOrder(input: { id: $id, status: $status }) {
                id
                status
            }
        }
        """
        payload = {
            "query": mutation,
            "variables": {"id": order_id, "status": new_status}
        }
        try:
            response = requests.post(url, json=payload, headers=SyncEngine.get_headers(), timeout=10)
            return response.json()
        except Exception as e:
            logger.error(f"❌ خطأ تحديث الحالة في قمرة للطلب {order_id}: {e}")
            raise e

    @staticmethod
    def cancel_order(order_id):
        """إرسال أمر إلغاء الطلب السيادي إلى قمرة عبر الـ Mutation"""
        return SyncEngine.update_order_status(order_id, "cancelled")

    @staticmethod
    def mark_as_fulfilled(order_id):
        """تحديث حالة الطلب إلى مشحون ومجهز في خوادم قمرة"""
        return SyncEngine.update_order_status(order_id, "delivered")
