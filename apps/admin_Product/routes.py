# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from apps.admin_Product import admin_product_bp
from apps.services.graphql_client import GraphQLClient # افترضت وجود خدمة العميل هنا

@admin_product_bp.route('/', methods=['GET'])
@login_required
def manage_products():
    page = request.args.get('page', 1, type=int)
    # تم تغيير استقبال المعامل من search إلى title ليتطابق مع القالب
    search = request.args.get('title', '').strip()
    
    # تجهيز متغيرات الطلب للـ GraphQL
    variables = {
        "input": {
            "page": page,
            "limit": 100,
            "title": search if search else None
        }
    }
    
    # هنا يتم استدعاء الـ API الخاص بك لجلب المنتجات
    # تأكد أن دالة جلب البيانات تستخدم 'variables' الموضحة أعلاه
    # response = GraphQLClient.execute_query("GET_ALL_PRODUCTS", variables)
    
    # للتمثيل فقط:
    products = [] # استبدلها ببياناتك القادمة من الـ API
    pagination = {"currentPage": page, "totalPages": 1} # استبدلها ببيانات الترقيم الحقيقية
    
    return render_template(
        'admin/admin_product.html',
        products=products,
        pagination=pagination,
        search=search # تمرير قيمة البحث للقالب للحفاظ عليها في الحقل
    )

@admin_product_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    # كود إضافة منتج
    return render_template('admin/add_product.html')

@admin_product_bp.route('/edit/<qid>', methods=['GET', 'POST'])
@login_required
def edit_product(qid):
    # كود تعديل منتج
    return render_template('admin/edit_product.html', qid=qid)
