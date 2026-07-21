# coding: utf-8
# 📂 apps/admin_Product/routes.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from apps.services.product_sync_service import ProductSyncService

# إنشاء Blueprint خاص بالمنتجات مع تحديد مجلد القوالب الصحيح
admin_product_bp = Blueprint(
    "admin_product_bp",
    __name__,
    url_prefix="/admin/products",
    template_folder="templates"  # هذا يضمن أن Flask يبحث داخل apps/admin_Product/templates
)

# 🟣 صفحة إدارة المنتجات (عرض مباشر من الـ API)
@admin_product_bp.route("/", methods=["GET"])
def manage_products():
    search = request.args.get("title", "")
    page = int(request.args.get("page", 1))

    service = ProductSyncService(token="YOUR_API_TOKEN")
    products_response = service.fetch_products(page=page, limit=20)

    # 🛡️ تحقق من الاستجابة
    products = products_response.get("data", [])
    pagination = products_response.get("pagination", None)

    if not products:
        flash("⚠️ لم يتم جلب أي منتجات من المتجر الخارجي أو حدث خطأ في الاتصال.", "warning")

    return render_template(
        "admin/admin_Product.html",
        products=products,
        pagination=pagination,
        search=search
    )

# 🟣 صفحة إضافة منتج يدوي (عرض فقط، بدون حفظ داخلي)
@admin_product_bp.route("/add", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        flash("تمت إضافة المنتج بنجاح ✅ (عرض فقط، لا حفظ داخلي)", "success")
        return redirect(url_for("admin_product_bp.manage_products"))
    return render_template("admin/add_product.html")

# 🟣 صفحة تعديل منتج (عرض مباشر من الـ API)
@admin_product_bp.route("/edit/<string:qid>", methods=["GET", "POST"])
def edit_product(qid):
    service = ProductSyncService(token="YOUR_API_TOKEN")
    product_response = service.fetch_product_by_qid(qid)

    product = None
    if product_response:
        product = product_response.get("data", None)
    else:
        flash("⚠️ لم يتم العثور على المنتج أو حدث خطأ في الاتصال.", "warning")

    if request.method == "POST":
        flash("تم تعديل المنتج بنجاح ✅ (عرض فقط، لا حفظ داخلي)", "success")
        return redirect(url_for("admin_product_bp.manage_products"))

    return render_template("admin/edit_product.html", product=product)

# 🟣 زر المزامنة (من الـ Modal) - مزامنة لحظية
@admin_product_bp.route("/sync", methods=["POST"])
def sync_products():
    service = ProductSyncService(token="YOUR_API_TOKEN")
    products_response = service.fetch_products(page=1, limit=100)  # جلب مباشر من الـ API

    if not products_response.get("data"):
        flash("⚠️ فشلت المزامنة اللحظية مع المتجر الخارجي.", "danger")
    else:
        flash("✅ تمت المزامنة اللحظية مع المتجر الخارجي", "success")

    return redirect(url_for("admin_product_bp.manage_products"))
