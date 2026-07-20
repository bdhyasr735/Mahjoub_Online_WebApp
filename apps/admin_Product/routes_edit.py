from flask import render_template, request, redirect, url_for, flash
from .routes import admin_product_bp


@admin_product_bp.route('/edit/<qid>', methods=['GET', 'POST'])
def edit_product(qid):
    """
    مسار تعديل بيانات منتج موجود بناءً على المعرّف (qid).
    - GET: جلب بيانات المنتج من قاعدة البيانات/الخدمة وتغذية نموذج التعديل.
    - POST: استقبال التعديلات والتحقق منها ثم حفظ التغييرات.
    """
    if request.method == 'POST':
        try:
            # 1. استخراج البيانات المحدثة من النموذج
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            price = request.form.get('price', type=float, default=0.0)
            quantity = request.form.get('quantity', type=int, default=0)
            category_id = request.form.get('category_id', '').strip()
            image_url = request.form.get('image_url', '').strip()

            # 2. التحقق من البيانات (Validation)
            if not title:
                flash('عفواً، لا يمكن ترك عنوان المنتج فارغاً.', 'danger')
                return redirect(url_for('admin_product_bp.edit_product', qid=qid))

            if price <= 0:
                flash('يرجى كتابة سعر صحيح للمنتج.', 'warning')
                return redirect(url_for('admin_product_bp.edit_product', qid=qid))

            # 3. تجهيز كائن التحديث (Payload)
            update_payload = {
                "qid": qid,
                "title": title,
                "description": description,
                "pricing": {
                    "price": price
                },
                "quantity": quantity,
                "category_id": category_id,
                "images": [{"fileUrl": image_url}] if image_url else []
            }

            # -------------------------------------------------------------
            # 4. تنفيذ استعلام التحديث (سواء GraphQL Mutation أو SQL Update)
            # example: response = update_product_in_db(qid, update_payload)
            # -------------------------------------------------------------

            flash('تم تحديث بيانات المنتج بنجاح!', 'success')
            return redirect(url_for('admin_product_bp.manage_products'))

        except Exception as e:
            flash(f'حدث خطأ أثناء تعديل المنتج: {str(e)}', 'danger')
            return redirect(url_for('admin_product_bp.edit_product', qid=qid))

    # -------------------------------------------------------------
    # حالة GET: جلب تفاصيل المنتج الحالية عبر الـ qid لعرضها في النموذج
    # -------------------------------------------------------------
    # product = get_product_by_qid(qid)
    product = {
        "qid": qid,
        "title": "",
        "description": "",
        "pricing": {"price": 0.0},
        "quantity": 0,
        "images": []
    }

    if not product:
        flash('المنتج المطلوب غير موجود أو تم حذفه.', 'warning')
        return redirect(url_for('admin_product_bp.manage_products'))

    return render_template('admin/edit_product.html', product=product, qid=qid)
