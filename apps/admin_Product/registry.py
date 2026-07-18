# coding: utf-8
# 📂 apps/admin_Product/registry.py

from flask import Blueprint, render_template, request
from flask_login import login_required
from apps.services.graphql_client import QomrahGraphQLClient
import logging

# 1. تعريف الـ Blueprint وتجهيز الـ Logger
admin_product_bp = Blueprint('admin_product_bp', __name__, template_folder='templates')
logger = logging.getLogger(__name__)

# 2. استيراد المسارات والملفات الفرعية لتسجيلها داخل الـ Blueprint
from . import routes_add, routes_edit, routes_sync

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    # استقبال رقم الصفحة وكلمة البحث (يدعم title و search لضمان التوافق مع الواجهة)
    page = request.args.get('page', 1, type=int)
    search = request.args.get('title', request.args.get('search', '')).strip()
    
    # رفع حد الجلب لـ 100 منتج عند البحث لضمان إمساك وتصفية العناصر محلياً بكفاءة
    limit = 100 if search else 20
    
    variables = {"input": {"page": page, "limit": limit}}
    if search:
        variables["input"]["title"] = search
    
    # استعلام جلب المنتجات من قمرة
    query = """
    query Data($input: GetAllProductsInput) {
      findAllProducts(input: $input) {
        data { qid, title, quantity, pricing { price }, images { fileUrl } }
        pagination { totalPages, currentPage, totalItems }
      }
    }
    """
    
    try:
        result = QomrahGraphQLClient.execute_query(query, variables=variables) or {}
    except Exception as e:
        logger.error(f"❌ GraphQL Error inside registry: {e}")
        result = {}

    data = result.get('findAllProducts', {})
    all_products = data.get('data', []) or []
    pag_info = data.get('pagination', {"totalPages": 1, "currentPage": 1, "totalItems": 0})
    
    # --- آلية الفلترة النصية المحلية الفورية لضمان عمل البحث ---
    if search:
        products = [
            p for p in all_products 
            if p.get('title') and search.lower() in str(p.get('title')).lower()
        ]
        # إعادة تهيئة الترقيم لصفحة واحدة عند ظهور النتائج المفلترة مخصصة
        pag_info = {"totalPages": 1, "currentPage": 1, "totalItems": len(products)}
    else:
        products = all_products
    
    return render_template('admin/admin_Product.html', 
                           products=products, 
                           pagination=pag_info, 
                           search=search)

# --- إعدادات ربط وتسجيل الموديول مع النظام واللوحة الرئيسية ---
MODULE_NAME = "إدارة المنتجات"
MODULE_ICON = "fas fa-box-open"
SHOW_IN_SUPPLIER = False 

LINKS = {
    "admin_product_bp.manage_products": "قائمة المنتجات",
    "admin_product_bp.add_product": "إضافة منتج"
}

def register_module(app):
    """دالة تسجيل الـ Blueprint وتعيين المسار الموحد للمنتجات"""
    try:
        app.register_blueprint(admin_product_bp, url_prefix='/admin/products')
        print("✅ [Registry]: تم تسجيل موديول 'إدارة المنتجات' بنجاح عبر registry.py")
    except Exception as e:
        print(f"❌ [Registry Error]: فشل تسجيل موديول 'إدارة المنتجات': {e}")
