# -*- coding: utf-8 -*-
# 📂 apps/admin_produc/registry.py
"""
متجر محجوب أونلاين (www.mahjoub.online) - Qumra Cloud Sandbox
Registry file for admin_Product module and components.
"""

MODULE_NAME = "إدارة المنتجات والمتغيرات"
MODULE_ICON = "fas fa-boxes"
SHOW_IN_ADMIN = True

# الروابط الأساسية للوحدة لتظهر تلقائياً في القائمة الجانبية الديناميكية
LINKS = {
    'admin_product.list_products': 'قائمة المنتجات',
    'admin_product.new_product': 'إضافة منتج جديد'
}

# ميتاداتا الوحدة المتقدمة وقدراتها
MODULE_METADATA = {
    "id": "admin_Product",
    "version": "1.0.0",
    "description": "موديول إدارة المنتجات والمتغيرات الديناميكية لمتجر محجوب أونلاين المرتبط بـ قمرة كلاود (Qumra Cloud)",
    "author": "Mahjoub Online Engineering",
    "brand_color": "#4A154B",
    "store_url": "www.mahjoub.online",
    "backend_provider": "Qumra Cloud Sandbox (قمرة كلاود)",
    "sandbox_graphql_endpoint": "https://api.qumra.cloud/sandbox/graphql",
    "capabilities": [
        "PRODUCT_MANAGEMENT",
        "DYNAMIC_VARIANTS_ENGINE",
        "PRICE_AND_INVENTORY_SYNC",
        "MEDIA_AND_SEO_TAXONOMY",
        "QUMRA_GRAPHQL_MUTATIONS"
    ]
}

NAVIGATION = [
    {
        "id": "products_list",
        "title": "قائمة المنتجات",
        "endpoint": "admin_product.list_products",
        "url": "/admin/products",
        "icon": "fas fa-list",
        "active": True
    },
    {
        "id": "product_create",
        "title": "إضافة منتج جديد",
        "endpoint": "admin_product.new_product",
        "url": "/admin/products/new",
        "icon": "fas fa-plus-square",
        "active": False
    }
]

# قاموس صلاحيات المنتجات
PRODUCT_PERMISSIONS_REGISTRY = {
    'create_product': 'إنشاء منتج جديد',
    'edit_product': 'تعديل بيانات المنتج',
    'delete_product': 'حذف المنتجات',
    'manage_stock': 'إدارة المخزون والكميات',
    'view_product_cost': 'عرض تكلفة المنتجات'
}

# GraphQL Queries & Mutations for Qumra Cloud Sandbox integration
QUMRA_GRAPHQL_SCHEMAS = {
    "QUERY_GET_PRODUCTS": """
        query GetStoreProducts($storeId: String!, $first: Int) {
            store(id: $storeId) {
                products(first: $first) {
                    nodes {
                        id
                        title
                        slug
                        status
                        description
                        price
                        compareAtPrice
                        quantity
                        images {
                            fileUrl
                        }
                        collections
                        tags
                        variants {
                            id
                            name
                            type
                            price
                            quantity
                        }
                        createdAt
                        updatedAt
                    }
                }
            }
        }
    """,
    "MUTATION_CREATE_PRODUCT": """
        mutation CreateProductWithVariants($input: ProductInput!) {
            productCreate(input: $input) {
                product {
                    id
                    title
                    slug
                    status
                    price
                    compareAtPrice
                    quantity
                    variants {
                        id
                        name
                        type
                        price
                        quantity
                    }
                }
                userErrors {
                    field
                    message
                }
            }
        }
    """,
    "MUTATION_UPDATE_PRODUCT": """
        mutation UpdateProductWithVariants($id: ID!, $input: ProductInput!) {
            productUpdate(id: $id, input: $input) {
                product {
                    id
                    title
                    slug
                    status
                    price
                    compareAtPrice
                    quantity
                    variants {
                        id
                        name
                        type
                        price
                        quantity
                    }
                }
                userErrors {
                    field
                    message
                }
            }
        }
    """,
    "MUTATION_DELETE_PRODUCT": """
        mutation DeleteProduct($id: ID!) {
            productDelete(id: $id) {
                deletedProductId
                success
            }
        }
    """
}

def register_module(app):
    """
    دالة تسجيل الموديول والمكونات داخل تطبيق Flask الرئيسي
    """
    from apps.admin_product.routes import admin_product_bp
    
    if 'admin_product_bp' not in app.blueprints:
        app.register_blueprint(admin_product_bp, url_prefix='/admin/products')
        print(f"[admin_Product] ✅ تم تسجيل موديول المنتجات ومتغيراتها لمتجر محجوب أونلاين بنجاح.")
    
    return True
