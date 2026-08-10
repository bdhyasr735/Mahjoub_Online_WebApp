# coding: utf-8
# 📂 apps/admin_Product/services.py

from apps.services.graphql_client import GraphQLClient

class ProductService:
    """خدمة إدارة المنتجات عبر GraphQL"""

    @staticmethod
    def get_graphql_client():
        return GraphQLClient()

    @staticmethod
    def get_products_page(page=1, per_page=10, search=None, status=None, collection=None):
        """جلب صفحة المنتجات من قمره مع الفلاتر والبحث"""
        client = ProductService.get_graphql_client()
        # استعلام مبني على استعلام المنتجات السابق
        query = """
        query GetProducts($input: FindAllProductsInput!) {
            findAllProducts(input: $input) {
                data {
                    _id
                    title
                    slug
                    description
                    status
                    pricing {
                        price
                        compareAtPrice
                        originalPrice
                    }
                    images {
                        fileUrl
                    }
                    quantity
                }
                pagination {
                    totalItems
                    totalPages
                    currentPage
                    limit
                    hasNextPage
                }
            }
        }
        """
        # بناء متغيرات الإدخال
        input_vars = {"page": page, "limit": per_page}
        if search:
            input_vars["search"] = search
        if status and status != 'all':
            input_vars["status"] = status
        if collection and collection != 'all':
            input_vars["collection"] = collection

        data = client.execute(query, {"input": input_vars})
        if data and "findAllProducts" in data:
            result = data["findAllProducts"]
            return {
                'products': result.get('data', []),
                'pagination': result.get('pagination', {})
            }
        return {'products': [], 'pagination': {'totalPages': 1, 'currentPage': 1}}

    @staticmethod
    def get_collections():
        """جلب قائمة التصنيفات (مؤقتة – يمكن تطويرها لاحقاً)"""
        # يمكنك لاحقاً جلبها من GraphQL، حالياً نعيد قائمة ثابتة للتجربة
        return ["إلكترونيات", "ملابس", "أثاث", "ألعاب"]

    @staticmethod
    def get_tags():
        """جلب قائمة الوسوم"""
        return ["جديد", "عرض خاص", "الأكثر مبيعاً"]

    @staticmethod
    def create_product_data(data):
        """إنشاء منتج جديد باستخدام Mutation"""
        client = ProductService.get_graphql_client()
        # يمكنك هنا كتابة Mutation `createProduct` الخاص بقمره
        # حالياً نعيد كائناً وهمياً للتجربة
        return {"id": "new_prod_001", "title": data.get('title')}

    @staticmethod
    def update_product_data(product_id, data):
        """تحديث منتج"""
        # يمكنك هنا كتابة Mutation `updateProduct`
        return {"id": product_id, "title": data.get('title')}

    @staticmethod
    def delete_product_data(product_id):
        return True, {"id": product_id, "deleted": True}

    @staticmethod
    def toggle_product_status(product_id, new_status):
        return True, {"id": product_id, "status": new_status}

    @staticmethod
    def generate_slug(title):
        import re
        return re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
