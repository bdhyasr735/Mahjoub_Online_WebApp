@admin_product_bp.route('/save-sync', methods=['POST'])
@login_required
@csrf.exempt # سنحتاج للـ CSRF هنا لاحقاً، لكن لنبدأ بـ exempt للتشغيل
def save_sync():
    """مسار جديد يستقبل البيانات من المتصفح مباشرة ويحفظها"""
    try:
        data = request.json  # البيانات القادمة من fetch في الجافاسكربت
        products_data = data.get('products', [])
        
        if not products_data:
            return jsonify({"status": "error", "message": "لا توجد بيانات للمزامنة"})

        count = 0
        for item in products_data:
            product = Product.query.filter_by(qid=str(item.get('_id'))).first()
            if not product:
                new_product = Product(
                    qid=str(item.get('_id')),
                    title=item.get('title', 'منتج غير معرف'),
                    supplier_id=1,
                    sku=item.get('sku', 'N/A'),
                    cost_price=float(item.get('price', 0))
                )
                db.session.add(new_product)
                count += 1
            else:
                product.title = item.get('title', product.title)
                product.cost_price = float(item.get('price', product.cost_price))
        
        db.session.commit()
        return jsonify({"status": "success", "message": f"تم حفظ {count} منتج جديد وتحديث الباقي."})

    except Exception as e:
        db.session.rollback()
        logging.error(f"خطأ أثناء حفظ المزامنة: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
