# coding: utf-8
# 📂 apps/admin_Product/routes.py

import logging
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from apps.services.graphql_client import QomrahGraphQLClient
from apps.api.sync_engine import ProductSyncEngine

logger = logging.getLogger(__name__)

admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')

@admin_product_bp.app_context_processor
def inject_utils():
    return dict(max=max, min=min)

# كلاس مخصص للتعامل مع نظام الـ Cursors (pageInfo)
class PaginationMock:
    def __init__(self, page_info):
        self.has_next_page = page_info.get('hasNextPage', False)
        self.has_prev_page = page_info.get('hasPreviousPage', False)
    def has_prev(self): return self.has_prev_page
    def has_next(self): return self.has_next_page
    def prev_num(self): return 0 # سنعتمد على منطق Cursor في الـ API
    def next_num(self): return 0

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    search = request.args.get('search', '').strip()
    
    # الاستعلام الجديد بناءً على Schema الشركة
    query = """
    query SearchProducts($query: String, $first: Int) {
      findAllProducts(query: $query, first: $first, sortKey: TITLE, reverse: false) {
        edges {
          node {
            id
            title
            totalInventory
            priceRangeV2 { minVariantPrice { amount } }
            featuredImage { url }
            variants(first: 1) { edges { node { sku } } }
          }
        }
        pageInfo { hasNextPage, hasPreviousPage }
      }
    }
    """
    
    variables = {"query": search if search else "", "first": 10}
    
    try:
        result = QomrahGraphQLClient.execute_query(query, variables=variables)
        data = result.get('findAllProducts', {}) if result else {}
    except Exception as e:
        logger.error(f"GraphQL Error: {e}")
        data = {}
    
    # تحويل بيانات GraphQL (edges/node) إلى قائمة بسيطة (products)
    edges = data.get('edges', [])
    products = []
    for edge in edges:
        node = edge.get('node', {})
        # مواءمة الأسماء مع القالب الحالي
        products.append({
            "qid": node.get('id'),
            "title": node.get('title'),
            "quantity": node.get('totalInventory', 0),
            "pricing": {"price": node.get('priceRangeV2', {}).get('minVariantPrice', {}).get('amount', 0)},
            "images": [{"fileUrl": node.get('featuredImage', {}).get('url')}],
            "identification": {"sku": node.get('variants', {}).get('edges', [{}])[0].get('node', {}).get('sku', '---')}
        })
    
    pag_info = data.get('pageInfo', {})
    return render_template('admin/admin_Product.html', products=products, pagination=PaginationMock(pag_info))

@admin_product_bp.route('/add', methods=['GET'])
@login_required
def add_product():
    return render_template('admin/admin_add_product.html')

@admin_product_bp.route('/proxy-sync', methods=['POST'])
@login_required
def proxy_sync():
    try:
        # استعلام المزامنة متوافق مع الـ Schema الجديد
        query = """
        query {
          findAllProducts(first: 100, sortKey: TITLE, reverse: false) {
            edges {
              node { id, title, totalInventory, priceRangeV2 { minVariantPrice { amount } }, featuredImage { url }, variants(first: 1) { edges { node { sku } } } }
            }
          }
        }
        """
        result = QomrahGraphQLClient.execute_query(query)
        edges = result.get('findAllProducts', {}).get('edges', []) if result else []
        
        # تجهيز البيانات للمزامنة
        products_data = []
        for edge in edges:
            node = edge.get('node', {})
            products_data.append({
                "qid": node.get('id'),
                "title": node.get('title'),
                "quantity": node.get('totalInventory'),
                "pricing": {"price": node.get('priceRangeV2', {}).get('minVariantPrice', {}).get('amount')},
                "images": [{"fileUrl": node.get('featuredImage', {}).get('url')}],
                "identification": {"sku": node.get('variants', {}).get('edges', [{}])[0].get('node', {}).get('sku')}
            })
            
        count = ProductSyncEngine.process_products(products_data)
        return jsonify({"status": "success", "message": f"تمت المزامنة بنجاح: تم تحديث {count} منتج."})
    except Exception as e:
        logger.error(f"Sync Error: {e}")
        return jsonify({"status": "error", "message": "حدث خطأ أثناء معالجة البيانات"}), 500

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    return jsonify({"status": "success", "message": "تم التخطي"})
