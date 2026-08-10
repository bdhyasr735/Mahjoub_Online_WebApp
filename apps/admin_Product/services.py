# coding: utf-8
# 📂 apps/admin_Product/services.py

from apps.services.graphql_client import GraphQLClient

class ProductService:
    """خدمة تفاعلية لإدارة المنتجات عبر GraphQL"""

    @staticmethod
    def get_graphql_client():
        """الحصول على عميل GraphQL موحد (يستخدم نفس اتصال المنصة)"""
        return GraphQLClient()

    @staticmethod
    def get_products_page(page=1, per_page=10, search=None, status=None, collection=None):
        """جلب صفحة المنتجات (مؤقت ليعمل الموديول دون أخطاء)"""
        # هنا في المستقبل نضع استعلام GraphQL لجلب المنتجات
        # حالياً نعيد هيكل فارغ لمنع الخادم من الانهيار
        return {
            'products': [], 
            'pagination': {'total': 0, 'pages': 1, 'current': 1}
        }

    @staticmethod
    def get_collections():
        """جلب التصنيفات"""
        return []  # مؤقت

    @staticmethod
    def get_tags():
        """جلب الوسوم"""
        return []

    @staticmethod
    def create_product_data(data):
        """إنشاء منتج جديد (تطبيق الـ Mutation)"""
        # يحتاج لاستعلام createProduct داخل GraphQL
        return {"id": "test_prod_123", "title": data.get('title')}

    @staticmethod
    def update_product_data(product_id, data):
        """تحديث منتج"""
        return {"id": product_id, "title": data.get('title')}

    @staticmethod
    def delete_product_data(product_id):
        """حذف منتج"""
        return True, {"id": product_id, "deleted": True}

    @staticmethod
    def toggle_product_status(product_id, new_status):
        """تغيير الحالة"""
        return True, {"id": product_id, "status": new_status}

    @staticmethod
    def generate_slug(title):
        """توليد slug تلقائي"""
        import re
        return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
