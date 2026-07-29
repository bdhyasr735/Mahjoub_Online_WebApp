@admin_product_bp.route('/products/edit', methods=['GET'])
@login_required
def edit_product():
    # ... (التحقق من المستخدم والـ qid هنا)...

    # ✅ محاولة جلب المنتج مع الخيارات (آمنة 100%)
    try:
        product = services.variants.get_product_with_options_and_variants(qid)
    except Exception:
        product = None

    # ✅ إذا فشلت، استخدم الدالة الأساسية التي تجلب المنتج فقط
    if not product:
        print(f"ℹ️ [Fallback] استخدام الخدمة الأساسية لجلب المنتج {qid}")
        product = services.products.get_product_by_qid(qid)
    
    # باقي الكود كما هو (التحقق من وجود المنتج، جلب الموردين، إلخ...)
    if not product:
        flash("❌ لم يتم العثور على المنتج", "danger")
        return redirect(url_for('admin_product_bp.manage_products_view'))
    
    # ... (باقي الكود) ...
