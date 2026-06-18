# coding: utf-8
# 📂 apps/api/sync_engine.py - محرك المزامنة المستقر والمطابق لـ GraphQL الـ Sandbox (النسخة التصحيحية النهائية)

import requests
import logging
from datetime import datetime
from apps.models.orders_db import ProcessedOrder, db
from apps.models.sync_log import SyncLog  # استيراد نموذج السجلات لتوثيق العمليات والأخطاء

logger = logging.getLogger(__name__)

class SyncEngine:
    # 🎯 تعديل المسار ليتطابق مع الـ Endpoint الفعلي لبيئة الحوكمة والإدارة الخاصة بنظامك
    API_URL = "https://admin.mahjoub.online/graphql"  
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
        page = 1
        has_next_page = True
        total_synced = 0
        
        while has_next_page:
            logger.info(f"🔄 جاري جلب ومزامنة الصفحة: {page} باستخدام الهيكل والمطابقة المحدثة")
            
            # 🎯 الاستعلام المصحح والمطابق تماماً لقيود التحقق في الـ Sandbox
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
            
            payload = {
                'query': query, 
                'variables': {'page': page}
            }
            
            try:
                response = requests.post(
                    SyncEngine.API_URL, 
                    json=payload, 
                    headers=SyncEngine._get_headers(),
                    timeout=120  # 🎯 تم رفع المهلة من 30 إلى 120 ثانية لتجنب الـ Read Timeout ومنح الخادم وقت كافٍ
                )
                
                result = response.json()
                
                # التحقق الصارم من وجود أخطاء في الرد لمنع تعارض الحقول
                if 'errors' in result:
                    error_msg = f"❌ خطأ تدوين من سيرفر البوابة: {result['errors']}"
                    logger.error(error_msg)
                    
                    # توثيق الخطأ الداخلي في قاعدة البيانات
                    log_entry = SyncLog(status="failed", message=error_msg, page=page)
                    db.session.add(log_entry)
                    db.session.commit()
                    return False
                
                orders_data = result.get('data', {}).get('orders', [])
                if not orders_data:
                    logger.info("ℹ️ لم يتم العثور على أي طلبات إضافية بانتظار المزامنة.")
                    break
                    
                for item in orders_data:
                    id_api = item.get('id')
                    if not id_api:
                        continue
                        
                    # البحث عن الطلب محلياً أو إنشاء كائن جديد (Upsert)
                    order = ProcessedOrder.query.get(id_api)
                    if not order:
                        order = ProcessedOrder(id=id_api)
                        db.session.add(order)
                    
                    # 🧭 خريطة تحويل البيانات (Data Mapping) إلى حقول قاعدتك المحلية المستقلة
                    order.order_id = id_api.split('-')[-1] if '-' in id_api else id_api
                    
                    # قراءة الحالة الموحدة وتوزيعها محلياً لدعم الفلاتر الثلاثية بشكل مستقر
                    api_status = item.get('status', 'pending')
                    order.order_status = api_status
                    
                    if api_status == 'delivered':
                        order.financial_status = 'paid'
                        order.fulfillment_status = 'fulfilled'
                    elif api_status == 'cancelled':
                        order.financial_status = 'unpaid'
                        order.fulfillment_status = 'unfulfilled'
                    else:
                        order.financial_status = 'unpaid'
                        order.fulfillment_status = 'unfulfilled'
                        
                    # تفكيك كائن بيانات العميل المتداخل (Nested Customer Object)
                    customer_data = item.get('customer') or {}
                    order.customer_name = customer_data.get('name') or "عميل متجر محجوب"
                    order.customer_phone = customer_data.get('phone', '---')
                    order.customer_email = customer_data.get('email', '---')
                    
                    # تفكيك كائن العنوان الجغرافي (Nested Shipping Object)
                    shipping_data = item.get('shippingAddress') or {}
                    order.shipping_country = shipping_data.get('country', 'Yemen')
                    order.shipping_city = shipping_data.get('city', '---')
                    order.shipping_district = shipping_data.get('district', '---')
                    order.shipping_street = shipping_data.get('street', '---')
                    
                    # وسيلة الدفع والقيمة المالية (تُشفر تلقائياً بـ AES-256 عبر الـ Setter في الموديل)
                    order.payment_type = item.get('paymentMethod', 'manual')
                    order.total_price = float(item.get('total', 0.0))
                    
                    # معالجة تاريخ الإنشاء بأمان
                    created_at_str = item.get('createdAt')
                    if created_at_str:
                        try:
                            order.created_at_api = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                        except Exception:
                            order.created_at_api = datetime.utcnow()
                    else:
                        order.created_at_api = datetime.utcnow()
                    
                    total_synced += 1
                
                db.session.commit()
                
                # تسيير الصفحات التزامنية (Pagination)
                if len(orders_data) < 10:  # إذا كانت البيانات المرتدة أقل من الليميت فهذا يعني الوصول لنهاية الصفحات
                    has_next_page = False
                else:
                    page += 1
                    
            except Exception as e:
                db.session.rollback()
                error_context = f"❌ خطأ في المزامنة أو الاتصال بالشبكة: {str(e)}"
                logger.error(error_context)
                
                # توثيق انقطاع الاتصال تلقائياً في جدول الـ SyncLog للمراقبة
                log_entry = SyncLog(status="failed", message=error_context, page=page)
                db.session.add(log_entry)
                db.session.commit()
                return False
        
        # عند النجاح الكامل، وثق السجل الإيجابي بعدد الطلبات المتزامنة
        if total_synced > 0:
            log_entry = SyncLog(status="success", message=f"✅ تمت المزامنة بنجاح. إجمالي الطلبات المحدثة: {total_synced}", page=page)
            db.session.add(log_entry)
            db.session.commit()
            
        return True

    @staticmethod
    def _execute_mutation(mutation, variables):
        try:
            response = requests.post(
                SyncEngine.API_URL, 
                json={'query': mutation, 'variables': variables}, 
                headers=SyncEngine._get_headers(),
                timeout=120  # 🎯 تم زيادة مهلة الـ Mutations أيضاً لتطابق إعدادات الأمان الجديدة
            )
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.error(f"❌ خطأ أثناء تنفيذ الـ Mutation: {e}")
            return None

    @staticmethod
    def update_order_status(order_id, new_status):
        """تحديث حالة الطلب وإرسال التعديل الفوري عبر الـ Mutation إلى السيرفر"""
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
        """إرسال أمر إلغاء الطلب السيادي عبر الـ Mutation"""
        return SyncEngine.update_order_status(order_id, "cancelled")

    @staticmethod
    def mark_as_fulfilled(order_id):
        """تحديث حالة الطلب إلى مشحون ومجهز عبر الـ Mutation"""
        return SyncEngine.update_order_status(order_id, "delivered")
