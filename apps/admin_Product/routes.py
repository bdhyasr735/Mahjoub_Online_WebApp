# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from apps.services.graphql_client import QomrahGraphQLClient
import math

admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').lower()
    per_page = 20
    
    # 1. الاستعلام المفتوح لجلب كل المنتجات (بما فيها الجديدة)
    query = """
    query Data {
      findAllProducts(input: { limit: 99999 }) {
        data {
          qid, title, quantity, pricing { price }, 
          images { fileUrl }, identification { sku }
        }
      }
    }
    """
    
    # 2. تنفيذ الطلب (سيجلب أحدث نسخة دائماً من قمرة)
    result = QomrahGraphQLClient.execute_query(query)
    all_products = result.get('data', {}).get('findAllProducts', {}).get('data', []) if result else []
    
    # 3. الفلترة المحلية (إذا كان هناك بحث)
    if search:
        all_products = [p for p in all_products if search in p.get('title', '').lower() or 
                        (p.get('identification') and search in p['identification'].get('sku', '').lower())]
    
    # 4. الترقيم اليدوي
    total = len(all_products)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_products = all_products[start:end]
    
    # 5. كائن الترقيم
    class Pagination:
        def __init__(self, page, per_page, total):
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = math.ceil(total / per_page) if total > 0 else 1
        def has_next(self): return self.page < self.pages
        def has_prev(self): return self.page > 1
        def next_num(self): return self.page + 1
        def prev_num(self): return self.page - 1

    pagination = Pagination(page, per_page, total)
    
    return render_template('admin/admin_Product.html', 
                           products=paginated_products, 
                           pagination=pagination,
                           search=search)

@admin_product_bp.route('/proxy-sync', methods=['POST'])
@login_required
def proxy_sync():
    # هذا المسار أصبح لا يحتاج لعمل شيء لأن الصفحة الرئيسية تجلب كل شيء تلقائياً
    return jsonify({"status": "success", "message": "تم التحديث"})

@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    return jsonify({"status": "success", "message": "لا يوجد حفظ في قاعدة البيانات"})
