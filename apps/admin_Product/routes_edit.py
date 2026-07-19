# 📂 apps/admin_Product/routes_edit.py
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from .registry import admin_product_bp
from apps.services.graphql_client import QomrahGraphQLClient

@admin_product_bp.route('/edit/<qid>', methods=['GET', 'POST'])
@login_required
def edit_product(qid):
    # جلب تفاصيل المنتج الحالية
    if request.method == 'GET':
        query = "query Get($qid: ID!) { findProduct(qid: $qid) { title, pricing { price }, quantity } }"
        response = QomrahGraphQLClient.execute_query(query, {"qid": qid})
        product = response['data']['findProduct'] if response else {}
        return render_template('admin/edit_product.html', product=product, qid=qid)

    # تحديث المنتج
    if request.method == 'POST':
        update_data = {
            "title": request.form.get('title'),
            "pricing": {"price": float(request.form.get('price', 0))},
            "quantity": int(request.form.get('quantity', 0))
        }
        mutation = "mutation Update($qid: ID!, $input: UpdateProductInput!) { updateProduct(qid: $qid, input: $input) { qid } }"
        response = QomrahGraphQLClient.execute_query(mutation, {"qid": qid, "input": update_data})
        
        if response and 'data' in response:
            flash("تم تحديث المنتج بنجاح.")
            return redirect(url_for('admin_product_bp.manage_products'))
        
        flash("فشل التحديث.")
        return redirect(url_for('admin_product_bp.edit_product', qid=qid))
