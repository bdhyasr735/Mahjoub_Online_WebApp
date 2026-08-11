# -*- coding: utf-8 -*-
# 📂 apps/admin_product/routes.py
"""
المسارات (Routes): محطة عبور لنظام إدارة المنتجات.
"""

from flask import render_template, request, redirect, url_for, flash
from . import admin_product_bp
from .sync_service import SyncService   # ✅ استدعاء خدمة المزامنة بجانب الملف
from .registry import MODULE_METADATA

# -----------------------------------------------------------------------------
# GET: عرض جدول المنتجات (مزامنة مع Qumra Cloud)
# -----------------------------------------------------------------------------
@admin_product_bp.route('/', methods=['GET'])
@admin_product_bp.route('/list', methods=['GET'])
def list_products():
    """
    استدعاء خدمة المزامنة لجلب الفلاتر والمنتجات والإحصائيات.
    """
    # 1. جلب معاملات الفلترة من الرابط
    search_query = request.args.get('q', '').strip().lower()
    status_filter = request.args.get('status', 'ALL')
    collection_filter = request.args.get('collection', 'ALL')
    supplier_filter = request.args.get('supplier', 'ALL').strip()

    # 2. تمرير الطلب إلى الخدمة لمعالجة البيانات وإرجاعها جاهزة
    context = SyncService.get_products_dashboard_context(
        search_query=search_query,
        status_filter=status_filter,
        collection_filter=collection_filter,
        supplier_filter=supplier_filter
    )

    # 3. إضافة الإعدادات العامة وإرجاع القالب
    context.update({
        "brand_color": MODULE_METADATA.get("brand_color", "#4A154B"),
        "store_url": MODULE_METADATA.get("store_url", "https://mahjoub.online"),
        "sandbox_endpoint": MODULE_METADATA.get("sandbox_graphql_endpoint", "https://api.qumra.cloud/graphql")
    })

    return render_template('admin_product/products_list.html', **context)


# -----------------------------------------------------------------------------
# GET: نافذة إضافة/تعديل منتج
# -----------------------------------------------------------------------------
@admin_product_bp.route('/new', methods=['GET'])
def new_product():
    return render_template(
        'admin_product/product_form.html',
        product=None,
        is_edit=False,
        brand_color=MODULE_METADATA.get("brand_color", "#4A154B"),
        store_url=MODULE_METADATA.get("store_url", "https://mahjoub.online")
    )

@admin_product_bp.route('/<product_id>/edit', methods=['GET'])
def edit_product(product_id):
    product = SyncService.get_single_product(product_id) # استدعاء الخدمة لجلب منتج مفرد
    if not product:
        flash('عذراً، المنتج المطلوب غير موجود في قمرة كلاود.', 'error')
        return redirect(url_for('admin_product.list_products'))
        
    return render_template(
        'admin_product/product_form.html',
        product=product,
        is_edit=True,
        brand_color=MODULE_METADATA.get("brand_color", "#4A154B"),
        store_url=MODULE_METADATA.get("store_url", "https://mahjoub.online")
    )


# -----------------------------------------------------------------------------
# POST: إنشاء وتحديث وحذف المنتجات (ممرر مباشر للخدمة)
# -----------------------------------------------------------------------------
@admin_product_bp.route('/create', methods=['POST'])
def create_product():
    try:
        data = request.form if not request.is_json else request.get_json()
        result = SyncService.create_product(data)
        flash(result.get('message', 'تم الإنشاء بنجاح عبر قمرة كلاود!'), "success")
    except Exception as e:
        flash(f"خطأ أثناء الحفظ: {str(e)}", "error")
    return redirect(url_for('admin_product.list_products'))

@admin_product_bp.route('/<product_id>/update', methods=['POST'])
def update_product(product_id):
    try:
        data = request.form if not request.is_json else request.get_json()
        result = SyncService.update_product(product_id, data)
        flash(result.get('message', 'تم التحديث بنجاح!'), "success")
    except Exception as e:
        flash(f"خطأ أثناء التحديث: {str(e)}", "error")
    return redirect(url_for('admin_product.list_products'))

@admin_product_bp.route('/<product_id>/delete', methods=['POST', 'DELETE'])
def delete_product(product_id):
    try:
        result = SyncService.delete_product(product_id)
        flash(result.get('message', 'تم الحذف بنجاح!'), "success")
    except Exception as e:
        flash(f"خطأ أثناء الحذف: {str(e)}", "error")
    return redirect(url_for('admin_product.list_products'))

# ============================================================
# ✅ إضافة مسار مختبر GraphQL (Apollo Sandbox)
# ============================================================
@admin_product_bp.route('/graphql-sandbox', methods=['GET'])
def graphql_sandbox():
    """
    صفحة مختبر GraphQL التفاعلي داخل لوحة التحكم
    """
    return render_template('admin_product/graphql_sandbox.html')
