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

# كلاس مخصص يتوافق مع هيكلية Pagination الجديدة
class PaginationMock:
    def __init__(self, pagination):
        self.pagination = pagination or {}
    def has_prev(self): return self.pagination.get('currentPage', 1) > 1
    def has_next(self): return self.pagination.get('hasNextPage', False)
    def prev_num(self): return self.pagination.get('currentPage', 1) - 1
    def next_num(self): return self.pagination.get('currentPage', 1) + 1

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    page = int(request.args.get('page', 1))
    
    # الاستعلام المتوافق مع الـ Schema الجديدة
    query = """
    query Data($input: GetAllProductsInput) {
      findAllProducts(input: $input) {
        data {
          qid: qid
          title
          quantity
          pricing { price }
          identification { sku }
          images { fileUrl }
        }
        pagination {
          totalItems
          hasNextPage
          currentPage
        }
      }
    }
    """
    
    variables = {"input": {"page": page, "limit": 20}}
    
    try:
        # إرسال الطلب مع المتغيرات
        response = QomrahGraphQLClient.execute_query(query, variables=variables)
        result = response.get('findAllProducts', {}) if response else {}
    except Exception as e:
        logger.error(f"GraphQL Error: {e}")
        result = {}
    
    products = result.get('data', [])
    pagination_data = result.get('pagination', {})
    
    return render_template('admin/admin_Product.html', 
                           products=products, 
                           pagination=PaginationMock(pagination_data))

@admin_product_bp.route('/add', methods=['GET'])
@login_required
def add_product():
    return render_template('admin/admin_add_product.html')

@admin_product_bp.route('/proxy-sync', methods=['POST'])
@login_required
def proxy_sync():
    try:
        # استعلام لجلب البيانات للمزامنة (زيادة الـ limit لجلب أكبر قدر ممكن)
        query = """
        query Data($input: GetAllProductsInput) {
          findAllProducts(input: $input) {
            data {
              qid: qid
              title
              quantity
              pricing { price }
              identification { sku }
              images { fileUrl }
            }
          }
        }
        """
        result = QomrahGraphQLClient.execute_query(query, variables={"input": {"limit": 100}})
        products_data = result.get('findAllProducts', {}).get('data', []) if result else []
            
        count = ProductSyncEngine.process_products(products_data)
        return jsonify({"status": "success", "message": f"تمت المزامنة بنجاح: تم تحديث {count} منتج."})
    except Exception as e:
        logger.error(f"Sync Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    return jsonify({"status": "success", "message": "تم التخطي"})
