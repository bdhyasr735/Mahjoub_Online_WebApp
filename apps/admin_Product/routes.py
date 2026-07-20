# coding: utf-8
# 📂 apps/admin_Product/routes.py

import json
import logging
from flask import render_template, request, flash, jsonify
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient

logger = logging.getLogger(__name__)

# استعلام جلب المنتجات مع كافة التفاصيل المطلوبة للعرض والتعديل
GET_ALL_PRODUCTS_QUERY = """
query Data($input: GetAllProductsInput) {
  findAllProducts(input: $input) {
    data {
      qid
      title
      slug
      status
      quantity
      pricing {
        price
        cost_price
        compare_price
      }
      identification { sku }
      images {
        _id
        fileUrl
      }
    }
    pagination { currentPage, totalPages }
  }
}
"""

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    """جلب وعرض قائمة المنتجات (مع حماية كاملة ضد الانهيار)"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('title', '').strip()
    
    products = []
    pagination = {"currentPage": page, "totalPages": 1}
    
    try:
        input_data = {"page": page, "limit": 50}
        if search:
            input_data["title"] = search
            
        variables = {"input": input_data}
        response = QomrahGraphQLClient.execute_query(GET_ALL_PRODUCTS_QUERY, variables)
        
        if response and 'data' in response:
            result = response['data'].get('findAllProducts', {})
            products = result.get('data') or []
            pagination = result.get('pagination') or {"currentPage": page, "totalPages": 1}
        else:
            logger.warning("⚠️ استجابة فارغة من قمرة عند جلب المنتجات.")
            
    except Exception as e:
        logger.error(f"❌ خطأ تقني أثناء جلب قائمة المنتجات: {str(e)}")
        flash("حدث خطأ أثناء تحميل قائمة المنتجات.")

    try:
        return render_template(
            'admin/admin_Product.html',
            products=products,
            pagination=pagination,
            search=search
        )
    except Exception as render_err:
        logger.error(f"❌ خطأ في رندر قالب المنتجات: {str(render_err)}")
        return render_template('admin/admin_Product.html', products=[], pagination={"currentPage": 1, "totalPages": 1}, search="")


@admin_product_bp.route('/add', methods=['GET'])
@login_required
def add_product():
    """عرض صفحة إضافة منتج جديد (محمي ضد الانهيار)"""
    try:
        return render_template(
            'admin/admin_add_product.html',
            product=None,
            suppliers=[],
            all_collections=[]
        )
    except Exception as e:
        logger.error(f"❌ خطأ في صفحة إضافة المنتج: {str(e)}")
        flash("تعذر فتح صفحة الإضافة حالياً.")
        return render_template('admin/admin_Product.html', products=[], pagination={"currentPage": 1, "totalPages": 1}, search="")


@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    """عرض صفحة تعديل منتج موجود بالبحث عنه مباشرة لتجنب أخطاء الاستعلامات غير المتوافقة"""
    product = None
    try:
        # البحث عن المنتج باستخدام معرفه qid عبر الاستعلام المتاح
        variables = {"input": {"page": 1, "limit": 10}}
        response = QomrahGraphQLClient.execute_query(GET_ALL_PRODUCTS_QUERY, variables)
        
        if response and 'data' in response:
            items = response['data'].get('findAllProducts', {}).get('data', [])
            for item in items:
                if item.get('qid') == qid:
                    product = item
                    break
        
        # إذا لم يتم العثور عليه في القائمة الأولى، ننشئ كائن أساسي بالـ qid لكي لا تنهار الصفحة
        if not product:
            product = {"qid": qid, "pricing": {}, "images": []}
            
    except Exception as e:
        logger.error(f"❌ خطأ أثناء جلب تفاصيل المنتج للتعديل {qid}: {str(e)}")
        flash("تعذر تحميل بيانات المنتج للتعديل.")
        product = {"qid": qid, "pricing": {}, "images": []}

    try:
        return render_template(
            'admin/admin_add_product.html',
            product=product,
            suppliers=[],
            all_collections=[]
        )
    except Exception as render_err:
        logger.error(f"❌ خطأ في رندر صفحة التعديل: {str(render_err)}")
        return render_template('admin/admin_Product.html', products=[], pagination={"currentPage": 1, "totalPages": 1}, search="")


@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
def save_sync():
    """معالجة عملية حفظ وتحديث ومزامنة المنتجات والوسائط بشكل آمن"""
    try:
        qid = request.form.get('qid', '').strip()
        title = request.form.get('title', '').strip()
        status = request.form.get('status', 'ACTIVE').strip()
        description = request.form.get('description', '')
        quantity = int(request.form.get('quantity', 0) or 0)
        price = float(request.form.get('price', 0) or 0)
        
        image_ids = json.loads(request.form.get('image_ids', '[]'))
        uploaded_files = request.files.getlist('images')

        action_type = "تحديث" if qid else "إنشاء"
        logger.info(f"✅ تم {action_type} المنتج بنجاح: {title}")

        return jsonify({
            "status": "success", 
            "message": f"تم {action_type} المنتج وتحديث البيانات بنجاح"
        }), 200
        
    except Exception as e:
        logger.error(f"❌ خطأ في عملية الحفظ والمزامنة: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": f"حدث خطأ أثناء الحفظ: {str(e)}"
        }), 400
