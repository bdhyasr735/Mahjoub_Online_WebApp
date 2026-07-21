# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from apps.services.product_sync_service import ProductSyncService

# إنشاء Blueprint خاص بالمنتجات
admin_product_bp = Blueprint("admin_product_bp", __name__, url_prefix="/admin/products")

# 🟣 صفحة إدارة المنتجات
@admin_product_bp.route("/", methods=["GET"])
def manage_products():
    search = request.args.get("title", "")
    page = int(request.args.get("page", 1))

    service = ProductSyncService(token="YOUR_API_TOKEN")
    products_response = service.fetch_products(page=page, limit=20)

    products = products_response.get("data", [])
    pagination = products_response.get("pagination", None)

    return render_template(
        "admin/admin_Product.html",
        products=products,
        pagination=pagination,
        search=search
    )

# 🟣 صفحة إضافة منتج يدوي
@admin_product_bp.route("/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        # منطق إضافة المنتج لقاعدة البيانات الداخلية
        flash("تمت إضافة المنتج بنجاح ✅", "success")
        return redirect(url_for("admin_product_bp.manage_products"))
    return render_template("admin/add_product.html")

# 🟣 صفحة تعديل منتج
@admin_product_bp.route("/edit/<string:qid>", methods=["GET", "POST"])
def edit_product(qid):
    service = ProductSyncService(token="YOUR_API_TOKEN")
    product_response = service.fetch_product_by_qid(qid)

    product = product_response.get("data", None)

    if request.method == "POST":
        # منطق تعديل المنتج
        flash("تم تعديل المنتج بنجاح ✅", "success")
        return redirect(url_for("admin_product_bp.manage_products"))

    return render_template("admin/edit_product.html", product=product)

# 🟣 زر المزامنة (من الـ Modal)
@admin_product_bp.route("/sync", methods=["POST"])
def sync_products():
    service = ProductSyncService(token="YOUR_API_TOKEN")
    products_response = service.fetch_products(page=1, limit=100)  # جلب أول 100 منتج مثلاً
    service.sync_to_local_db(products_response)

    flash("تمت مزامنة المنتجات بنجاح ✅", "success")
    return redirect(url_for("admin_product_bp.manage_products"))
