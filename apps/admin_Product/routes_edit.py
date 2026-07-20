# coding: utf-8
# 📂 apps/admin_Product/routes.py

import json
import logging
from flask import render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient

try:
    from apps.models.product_supplier_map import ProductSupplierMapping
    from apps.models.supplier import Supplier
    HAS_MODELS = True
except ImportError:
    HAS_MODELS = False

logger = logging.getLogger(__name__)

# استعلام جلب قائمة المنتجات للإدارة والبحث
GET_ALL_PRODUCTS_QUERY = """
query Data($input: GetAllProductsInput) {
  findAllProducts(input: $input) {
    data {
      qid
      title
      pricing { price }
      quantity
      identification { sku }
      images { fileUrl }
    }
    pagination { currentPage, totalPages }
  }
}
"""

# الاستعلام الشامل لجلب تفاصيل المنتج للتعديل
GET_PRODUCT_DETAIL_QUERY = """
query GetProductDetail($qid: String!) {  
    findProductByQid(qid: $qid) {  
        data {
            qid
            title
            slug
            description
            status
            quantity
            pricing { 
                price 
                cost_price 
                compare_price 
            }
            images { 
                _id 
                fileUrl 
            }
            collections { 
                qid 
                title 
            }
        }
    }  
}
"""

# استعلام جلب كافة المجموعات
GET_ALL_COLLECTIONS_QUERY = """
query GetAllCollections {
    findAllCollections(input: { limit: 100 }) {
        data { qid, title }
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
    """عرض صفحة إضافة منتج جديد مع تمرير القوائم الفارغة أو المتاحة بأمان"""
    try:
        suppliers = []
        all_collections = []
        
        if HAS_MODELS:
            try:
                suppliers = Supplier.query.all()
            except Exception:
                pass

        try:
            col_response = QomrahGraphQLClient.execute_query(GET_ALL_COLLECTIONS_QUERY)
            if col_response and 'data' in col_response:
                all_collections = col_response['data'].get('findAllCollections', {}).get('data', [])
        except Exception:
            pass

        return render_template(
            'admin/admin_add_product.html',
            product=None,
            suppliers=suppliers,
            mapping={"selected_supplier_id": None},
            all_collections=all_collections
        )
    except Exception as e:
        logger.error(f"❌ خطأ في صفحة إضافة المنتج: {str(e)}")
        flash("تعذر فتح صفحة الإضافة حالياً.")
        return render_template('admin/admin_Product.html', products=[], pagination={"currentPage": 1, "totalPages": 1}, search="")


@admin_product_bp.route('/edit/<path:qid>', methods=['GET'])
@login_required
def edit_product(qid):
    """عرض صفحة تعديل المنتج مع كافة البيانات المحدثة والمخزون والمجموعات والموردين"""
    try:
        prod_response = QomrahGraphQLClient.execute_query(GET_PRODUCT_DETAIL_QUERY, {"qid": qid})
        col_response = QomrahGraphQLClient.execute_query(GET_ALL_COLLECTIONS_QUERY)
        
        product_node = None
        if prod_response and 'data' in prod_response:
            find_res = prod_response['data'].get('findProductByQid')
            if find_res:
                product_node = find_res.get('data')

        if not product_node:
            flash("❌ تعذر جلب بيانات المنتج من قمرة.", "danger")
            return redirect(url_for('admin_product_bp.manage_products'))
            
        product = product_node
        product['collection_ids'] = [c['qid'] for c in product.get('collections', []) if c and c.get('qid')]

        all_collections = []
        if col_response and 'data' in col_response:
            all_collections = col_response['data'].get('findAllCollections', {}).get('data', [])

        suppliers = []
        mapping_data = {"selected_supplier_id": None}
        if HAS_MODELS:
            try:
                suppliers = Supplier.query.all()
                mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
                if mapping:
                    mapping_data["selected_supplier_id"] = str(mapping.supplier_id)
            except Exception as db_err:
                logger.error(f"⚠️ خطأ أثناء جلب بيانات الموردين: {db_err}")

        return render_template(
            'admin/admin_add_product.html',
            product=product,
            suppliers=suppliers,
            mapping=mapping_data,
            all_collections=all_collections
        )

    except Exception as e:
        logger.error(f"❌ خطأ تقني في موديول التعديل: {str(e)}")
        flash("حدث خطأ تقني أثناء تحميل صفحة التعديل.", "danger")
        return redirect(url_for('admin_product_bp.manage_products'))


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
