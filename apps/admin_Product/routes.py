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

class PaginationMock:
    def __init__(self, p):
        # تأكد من مطابقة أسماء الحقول التي يعيدها الـ API (قد تكون edges/node أو data/pagination)
        self.page = p.get('currentPage', 1)
        self.pages = p.get('totalPages', 1)
        self.total = p.get('totalItems', 0)
    def has_prev(self): return self.page > 1
    def has_next(self): return self.page < self.pages
    def prev_num(self): return self.page - 1
    def next_num(self): return self.page + 1

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    
    # بناء الاستعلام حسب توجيه الشركة: query و first/limit كوسطاء مباشرة
    query = """
    query Data($query: String, $page: Int, $limit: Int) {
      findAllProducts(query: $query, page: $page, limit: $limit) {
        data { qid, title, quantity, pricing { price }, images { fileUrl }, identification { sku } }
        pagination { totalPages, currentPage, totalItems }
      }
    }
    """
    
    # تمرير المتغيرات كما طلبت الشركة (بدون input)
    variables = {
        "query": search if search else None,
        "page": page,
        "limit": 10
    }
    
    try:
        result = QomrahGraphQLClient.execute_query(query, variables=variables)
        logger.info(f"GraphQL Query executed with search: {search}")
    except Exception as e:
        logger.error(f"GraphQL Error: {e}")
        result = {}
    
    data = result.get('findAllProducts', {}) if result else {}
    products = data.get('data', [])
    pag_info = data.get('pagination', {"totalPages": 1, "currentPage": 1, "totalItems": 0})
    
    return render_template('admin/admin_Product.html', 
                           products=products, 
                           pagination=PaginationMock(pag_info))

@admin_product_bp.route('/add', methods=['GET'])
@login_required
def add_product():
    return render_template('admin/admin_add_product.html')

@admin_product_bp.route('/proxy-sync', methods=['POST'])
@login_required
def proxy_sync():
    try:
        # المزامنة تستخدم نفس الدالة بدون وسيط query
        query = """
        query {
          findAllProducts(limit: 100) {
            data { 
                qid, title, quantity, 
                pricing { price }, 
                identification { sku }, 
                weight { weight, unit }, 
                images { fileUrl } 
            }
          }
        }
        """
        result = QomrahGraphQLClient.execute_query(query)
        if not result or 'findAllProducts' not in result:
            return jsonify({"status": "error", "message": "فشل الاتصال بـ قمرة"}), 500
        
        products_data = result['findAllProducts'].get('data', [])
        count = ProductSyncEngine.process_products(products_data)
        return jsonify({"status": "success", "message": f"تمت المزامنة بنجاح: تم تحديث {count} منتج."})
    except Exception as e:
        logger.error(f"Sync Error: {e}")
        return jsonify({"status": "error", "message": "حدث خطأ أثناء معالجة البيانات"}), 500

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    return jsonify({"status": "success", "message": "تم التخطي"})
