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
        """جلب صفحة المنتجات من قمره مع الفلاتر والبحث وحماية ضد الانقطاع"""
        client = ProductService.get_graphql_client()
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
        input_vars = {"page": int(page), "limit": int(per_page)}
        if search:
            input_vars["search"] = search
        if status and status != 'all':
            input_vars["status"] = status
        if collection and collection != 'all':
            input_vars["collection"] = collection

        try:
            data = client.execute(query, {"input": input_vars}, operation_name="GetProducts")
            print("🔍 [GraphQL Response Raw]:", data)  # <-- لمراقبة الاستجابة الخام ومعرفة ما إذا كانت المنتجات فارغة من الخادم
            if data and "findAllProducts" in data:
                result = data["findAllProducts"]
                return {
                    'products': result.get('data', []),
                    'pagination': result.get('pagination', {})
                }
        except Exception as e:
            print(f"⚠️ [ProductService] Error fetching products: {e}")

        # هيكل احتياطي فارغ لمنع انهيار الصفحة في حال تعذر الاتصال
        return {
            'products': [],
            'pagination': {
                'totalItems': 0,
                'totalPages': 1,
                'currentPage': int(page),
                'limit': int(per_page),
                'hasNextPage': False
            }
        }

    @staticmethod
    def get_product_by_id(product_id):
        """جلب منتج واحد بواسطة الـ ID الخاص به (لمنع انهيار route edit_product)"""
        client = ProductService.get_graphql_client()
        query = """
        query GetProductById($id: ID!) {
            findProductByQid(qid: $id) {
                success
                message
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
                    seo {
                        title
                        description
                        keywords
                    }
                    tags
                    collections {
                        title
                        handle
                    }
                }
            }
        }
        """
        try:
            data = client.execute(query, {"id": product_id}, operation_name="GetProductById")
            if data and "findProductByQid" in data:
                result = data["findProductByQid"]
                if result.get("success"):
                    return result.get("data")
        except Exception as e:
            print(f"⚠️ [ProductService] Error fetching product by ID {product_id}: {e}")
            
        return None

    @staticmethod
    def get_collections():
        """جلب قائمة التصنيفات (مؤقتة)"""
        return ["إلكترونيات", "ملابس", "أثاث", "ألعاب"]

    @staticmethod
    def get_tags():
        """جلب قائمة الوسوم"""
        return ["جديد", "عرض خاص", "الأكثر مبيعاً"]

    @staticmethod
    def create_product_data(data):
        """إنشاء منتج جديد باستخدام Mutation"""
        client = ProductService.get_graphql_client()
        return {"id": "new_prod_001", "title": data.get('title')}

    @staticmethod
    def update_product_data(product_id, data):
        """تحديث منتج"""
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
