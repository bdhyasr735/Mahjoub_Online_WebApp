"""
متجر محجوب أونلاين (www.mahjoub.online) - Qumra Cloud Sandbox
Registry file for admin_Product module and components.
"""

MODULE_METADATA = {
    "id": "admin_Product",
    "name": "إدارة المنتجات والمتغيرات",
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
        "icon": "package-list",
        "active": True
    },
    {
        "id": "product_create",
        "title": "إضافة منتج جديد",
        "endpoint": "admin_product.new_product",
        "url": "/admin/products/new",
        "icon": "plus-square",
        "active": False
    }
]

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
    from . import admin_product_bp
    app.register_blueprint(admin_product_bp)
    print(f"[admin_Product] ✅ تم تسجيل موديول المنتجات ومتغيراتها لمتجر محجوب أونلاين بنجاح.")
    return True
ن