# -*- coding: utf-8 -*-
# 📂 apps/admin_product/sync_service.py
"""
خدمة المزامنة (Sync Service): التعامل المباشر مع GraphQL ومحطة العبور.
لا يحفظ أي بيانات محلياً، بل يمرر الطلبات ويحسب الإحصائيات لحظياً.
"""

from apps.services.product_service import ProductService
from apps.services.collection_service import CollectionService

class SyncService:
    
    @classmethod
    def get_products_dashboard_context(cls, search_query, status_filter, collection_filter, supplier_filter):
        """
        جلب البيانات وتصفيتها وحساب الإحصائيات لعرضها في واجهة لوحة القيادة.
        """
        # 1. جلب المنتجات الخام من قمرة كلاود عبر خدمة المنتجات
        raw_data = ProductService.get_all_products()
        
        # معالجة هيكل البيانات (حسب ما أرسلته في `graphql_client.py` ترجع `findAllProducts`)
        # نتعامل مع المرونة: سواء كانت القائمة تحت مفتاح 'data' أو مباشرة
        products = []
        if raw_data and isinstance(raw_data, dict):
            products = raw_data.get('data', [])
        elif isinstance(raw_data, list):
            products = raw_data
        
        # 2. تطبيق الفلاتر
        filtered_products = []
        for p in products:
            matches_search = (
                search_query in p.get('title', '').lower() or
                search_query in p.get('slug', '').lower() or
                search_query in p.get('sku', '').lower() or
                search_query in p.get('supplier_name', '').lower()
            ) if search_query else True
            
            matches_status = (p.get('status') == status_filter) if status_filter != 'ALL' else True
            matches_collection = (collection_filter in p.get('collections', [])) if collection_filter != 'ALL' else True
            
            matches_supplier = True
            if supplier_filter == 'ADMIN':
                matches_supplier = (p.get('supplier_id') is None)
            elif supplier_filter == 'SUPPLIERS':
                matches_supplier = (p.get('supplier_id') is not None)
            elif supplier_filter != 'ALL':
                matches_supplier = (str(p.get('supplier_id')) == supplier_filter)

            if matches_search and matches_status and matches_collection and matches_supplier:
                filtered_products.append(p)

        # 3. حساب الإحصائيات (داخل الذاكرة فقط)
        total_products = len(products)
        admin_tracking_count = sum(1 for p in products if p.get('supplier_id') is None)
        supplier_tracking_count = sum(1 for p in products if p.get('supplier_id') is not None)
        total_variants = sum(len(p.get('variants', [])) for p in products)
        total_stock_qty = sum(p.get('quantity', 0) for p in products)

        # 4. جمع المجموعات وبناء خريطة الموردين (لكي تظهر في الفلاتر)
        all_collections = set()
        suppliers_map = {}
        for p in products:
            for c in p.get('collections', []):
                all_collections.add(c)
            sid = p.get('supplier_id')
            sname = p.get('supplier_name')
            if sid is not None and sname:
                suppliers_map[str(sid)] = sname

        # 5. إرجاع الهيكل الجاهز للـ Dashboard
        return {
            "products": filtered_products,
            "total_products": total_products,
            "active_products": sum(1 for p in products if p.get('status') == 'ACTIVE'),
            "admin_tracking_count": admin_tracking_count,
            "supplier_tracking_count": supplier_tracking_count,
            "total_variants": total_variants,
            "total_stock_qty": total_stock_qty,
            "collections": list(all_collections),
            "suppliers_map": suppliers_map,
            "search_query": search_query,
            "current_status": status_filter,
            "current_collection": collection_filter,
            "current_supplier": supplier_filter,
        }

    @classmethod
    def get_single_product(cls, product_id):
        """جلب منتج واحد لتعبئة نموذج التعديل."""
        try:
            return ProductService.get_product_by_id(product_id)
        except Exception:
            return None

    @classmethod
    def create_product(cls, data):
        """إنشاء منتج عبر المزامنة."""
        return ProductService.create_product(data)

    @classmethod
    def update_product(cls, product_id, data):
        """تحديث منتج عبر المزامنة."""
        return ProductService.update_product(product_id, data)

    @classmethod
    def delete_product(cls, product_id):
        """حذف منتج عبر المزامنة."""
        return ProductService.delete_product(product_id)
