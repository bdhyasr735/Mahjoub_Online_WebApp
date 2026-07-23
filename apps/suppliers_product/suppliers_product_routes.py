# ============================================================
# 🟣 مسار إضافة منتج جديد
# ============================================================
@suppliers_product_bp.route('/add-product', methods=['GET'])
@login_required
def add_product():
    """صفحة إضافة منتج جديد للمورد"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)
        
        if user_type == 'staff':
            supplier_id = current_user.supplier_id
        else:
            supplier_id = current_user.id
        
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            abort(404)
        
        return render_template(
            'suppliers/add_product.html',
            supplier=supplier
        )
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في add_product: {error_details}")
        return f"❌ خطأ: {error_details}", 500


# ============================================================
# 🟣 مسار حفظ منتج جديد (POST)
# ============================================================
@suppliers_product_bp.route('/add-product', methods=['POST'])
@login_required
def save_product():
    """حفظ منتج جديد للمورد"""
    try:
        user_type = session.get('user_type')
        if user_type not in ['supplier', 'staff']:
            abort(403)
        
        if user_type == 'staff':
            supplier_id = current_user.supplier_id
        else:
            supplier_id = current_user.id
        
        name = request.form.get('name', '').strip()
        cost_price = request.form.get('cost_price', '').strip()
        
        if not name:
            return "❌ اسم المنتج مطلوب", 400
        
        if not cost_price or float(cost_price) <= 0:
            return "❌ سعر التكلفة يجب أن يكون أكبر من 0", 400
        
        # ✅ هنا يتم رفع المنتج إلى Qumra
        # ... منطق المزامنة مع Qumra ...
        
        return redirect(url_for('suppliers_product_bp.products'))
        
    except Exception as e:
        error_details = traceback.format_exc()
        print(f"❌ خطأ في save_product: {error_details}")
        return f"❌ خطأ: {error_details}", 500
