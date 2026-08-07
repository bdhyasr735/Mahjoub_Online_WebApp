# coding: utf-8
# 📂 apps/services/order_service.py
# خدمة جلب الطلبات من المصدر الخارجي (GraphQL API) ومعالجة البيانات

import requests
import json
import traceback
from flask import current_app

class OrderService:
    """
    خدمة التعامل مع الطلبات من واجهة برمجة التطبيقات (API) الخارجية.
    تتولى عمليات المصادقة، الاستعلام، وتنظيم البيانات.
    """

    # ✅ هذا هو التعديل الجذري: إضافة client=None ليستقبل الوسيط ولا ينهار
    def __init__(self, client=None):
        if client:
            self.client = client
        else:
            self.client = None
            
        # 🔑 إعدادات الاتصال بالسيرفر الخارجي
        # ضع هنا الرابط والـ Token الحقيقيين الخاصين بـ "قمره"
        self.api_url = "https://api.mahjoub-sa.com/graphql"  
        self.access_token = "YOUR_API_TOKEN_HERE" 

    def _execute_graphql_query(self, query, variables=None):
        """
        دالة مساعدة لتنفيذ استعلامات GraphQL وإرجاع النتيجة
        مع التقاط الأخطاء لطباعتها في الـ Logs.
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "query": query,
            "variables": variables or {}
        }

        try:
            # إرسال الطلب
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=30)
            
            # ✅ طباعة الاستجابة الخام في سجل الخادم (مهم جداً للتصحيح)
            print(f"\n🔍 [OrderService DEBUG] Request URL: {self.api_url}")
            print(f"🔍 [OrderService DEBUG] Status Code: {response.status_code}")
            if response.status_code != 200:
                print(f"❌ [OrderService DEBUG] Response Text: {response.text}")
                return None

            result = response.json()
            
            if 'errors' in result:
                print(f"❌ [OrderService DEBUG] GraphQL Errors: {json.dumps(result['errors'], indent=2)}")
                return None
            
            return result.get('data')

        except requests.exceptions.RequestException as req_err:
            print(f"❌ [OrderService] فشل الاتصال بالسيرفر الخارجي: {req_err}")
            traceback.print_exc()
            return None
        except json.JSONDecodeError as json_err:
            print(f"❌ [OrderService] خطأ في قراءة JSON القادم من السيرفر: {json_err}")
            return None
        except Exception as e:
            print(f"❌ [OrderService] خطأ غير متوقع في جلب البيانات: {e}")
            traceback.print_exc()
            return None

    def get_all_orders(self, page=1, limit=50):
        query = """
        query GetOrders($page: Int, $limit: Int) {
            orders(page: $page, limit: $limit) {
                data {
                    _id
                    orderNumber
                    orderReference
                    totalPrice
                    isPaid
                    createdAt
                    updatedAt
                    account {
                        account {
                            fullname
                            phone
                        }
                    }
                    shippingAddress {
                        street
                        description
                    }
                    status {
                        code
                        title
                    }
                    items {
                        productId
                        quantity
                        price
                        productData {
                            title
                            image {
                                fileUrl
                            }
                        }
                    }
                }
                pagination {
                    hasNextPage
                    totalCount
                }
            }
        }
        """
        
        variables = {"page": page, "limit": limit}
        data = self._execute_graphql_query(query, variables)

        if not data:
            return None
        return data.get('orders', {})

    def get_order_by_id(self, order_id):
        query = """
        query GetOrder($id: ID!) {
            order(id: $id) {
                _id
                orderNumber
                orderReference
                totalPrice
                isPaid
                createdAt
                updatedAt
                account {
                    account {
                        fullname
                        phone
                    }
                }
                shippingAddress {
                    street
                    description
                }
                status {
                    code
                    title
                }
                items {
                    productId
                    quantity
                    price
                    productData {
                        title
                        image {
                            fileUrl
                        }
                    }
                }
            }
        }
        """
        
        variables = {"id": order_id}
        data = self._execute_graphql_query(query, variables)
        if not data:
            return None
        return data.get('order')

# ✅ تعريف المتغير العام
orders_service = OrderService()

# ربط الدوال لتكون متاحة للاستيراد المباشر
def get_all_orders(page=1, limit=50):
    return orders_service.get_all_orders(page, limit)

def get_order_by_id(order_id):
    return orders_service.get_order_by_id(order_id)
