def manage_products_view():
    try:
        user_type = session.get('user_type')
        if user_type != 'admin':
            flash('❌ هذا القسم مخصص للإدارة فقط', 'danger')
            return redirect(url_for('admin_dashboard_bp.dashboard'))
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search_query = request.args.get('title', '', type=str)
        ajax = request.args.get('ajax', 0, type=int)
        
        # ✅ جلب المنتجات مع معلومات الترقيم
        result = services.products.get_all_products() or {}
        all_products = result.get('data', [])
        pagination_info = result.get('pagination', {})
        
        # ✅ استخدام totalItems من GraphQL إذا كان متاحاً
        total_products = pagination_info.get('totalItems', len(all_products))
        
        if search_query:
            all_products = [p for p in all_products if search_query.lower() in p.get('title', '').lower()]
            total_products = len(all_products)
        
        total_pages = (total_products + per_page - 1) // per_page if total_products > 0 else 1
        if page > total_pages:
            page = total_pages
        
        start = (page - 1) * per_page
        end = start + per_page
        products = all_products[start:end]
        
        # ✅ ربط الموردين
        for product in products:
            mapping = ProductSupplierMapping.query.filter_by(product_qid=product.get('qid')).first()
            if mapping:
                supplier = Supplier.query.get(mapping.supplier_id)
                product['supplier_name'] = supplier.trade_name if supplier else 'غير معروف'
                product['supplier_id'] = mapping.supplier_id
            else:
                product['supplier_name'] = 'غير مرتبط'
                product['supplier_id'] = None
        
        pagination_data = {
            "currentPage": page,
            "totalPages": total_pages,
            "limit": len(products),
            "totalItems": total_products,
            "perPage": per_page,
            "hasPrev": page > 1,
            "hasNext": page < total_pages
        }
        
        if ajax:
            return render_template('admin/includes/_table_products.html',
                                   products=products,
                                   search_title=search_query,
                                   pagination=pagination_data)
        
        return render_template('admin/admin_Product.html',
                               products=products,
                               search_title=search_query,
                               pagination=pagination_data)
    except Exception as e:
        print(f"❌ خطأ في manage_products: {e}")
        flash(f'❌ حدث خطأ في تحميل المنتجات: {str(e)}', 'danger')
        
        if ajax:
            return '<div class="alert alert-danger">حدث خطأ في تحميل المنتجات</div>'
        
        return render_template('admin/admin_Product.html',
                               products=[],
                               search_title=request.args.get('title', ''),
                               pagination={
                                   "currentPage": 1,
                                   "totalPages": 1,
                                   "limit": 0,
                                   "totalItems": 0,
                                   "hasPrev": False,
                                   "hasNext": False
                               })
