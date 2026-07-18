# coding: utf-8
import logging
from flask import render_template, request, jsonify
from flask_login import login_required
from apps.services.graphql_client import QomrahGraphQLClient
from .registry import admin_product_bp

logger = logging.getLogger(__name__)

@admin_product_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'GET':
        return render_template('admin/admin_add_product.html')

    # في حالة POST: استقبال البيانات من الفورم عبر AJAX
    data = request.json
    
    mutation = """
    mutation CreateProduct($input: CreateProductInput!) {
      createProduct(input: $input) {
        status
        message
      }
    }
    """
    
    try:
        # إرسال البيانات المدخلة إلى السيرفر
        result = QomrahGraphQLClient.execute_query(mutation, variables={"input": data}) or {}
        response = result.get('createProduct', {})
        
        if response.get('status') == 'success':
            return jsonify({"status": "success", "message": "تم إضافة المنتج بنجاح"})
        else:
            return jsonify({"status": "error", "message": response.get('message', 'فشل الإضافة')})
            
    except Exception as e:
        logger.error(f"Error adding product: {e}")
        return jsonify({"status": "error", "message": "خطأ في الاتصال بالسيرفر"}), 500
