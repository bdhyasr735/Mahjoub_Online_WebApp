# coding: utf-8
# 📂 apps/services/product_mapping_operations.py

from typing import Dict, List
from apps.extensions import db
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier import Supplier
from .graphql_client import QomrahGraphQLClient
from .product_mapping_service import product_mapping


class ProductMappingOperations:
    """عمليات متقدمة على علاقات الربط"""

    def __init__(self):
        self.client = QomrahGraphQLClient()

    # ============================================================
    # 🔍 VERIFICATION - التحقق من العلاقات
    # ============================================================

    def verify_mapping(self, product_qid: str) -> Dict:
        """التحقق من صحة العلاقة (وجود المنتج في قمرة)"""
        mapping = ProductSupplierMapping.query.filter_by(product_qid=product_qid).first()
        if not mapping:
            return {'valid': False, 'product': None, 'message': f'الربط غير موجود للمنتج {product_qid}'}

        product = self.client.get_product_by_qid(product_qid)
        if product:
            return {'valid': True, 'product': product, 'message': 'المنتج موجود في قمرة'}
        else:
            return {'valid': False, 'product': None, 'message': f'المنتج {product_qid} غير موجود في قمرة'}

    def verify_all_mappings(self) -> Dict:
        """التحقق من جميع العلاقات"""
        mappings = ProductSupplierMapping.query.all()
        results = {'total': len(mappings), 'valid': 0, 'invalid': 0, 'details': []}

        for mapping in mappings:
            result = self.verify_mapping(mapping.product_qid)
            results['details'].append({
                'id': mapping.id,
                'product_qid': mapping.product_qid,
                'supplier_id': mapping.supplier_id,
                'valid': result['valid'],
                'message': result['message']
            })
            if result['valid']:
                results['valid'] += 1
            else:
                results['invalid'] += 1

        return results

    # ============================================================
    # 📊 STATISTICS - إحصائيات
    # ============================================================

    def get_stats(self) -> Dict:
        """الحصول على إحصائيات العلاقات"""
        mappings = ProductSupplierMapping.query.all()
        stats = {'total': len(mappings), 'by_status': {}, 'by_supplier': {}, 'total_suppliers': 0}
        supplier_ids = set()

        for mapping in mappings:
            status = mapping.status
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1

            supplier_id = mapping.supplier_id
            supplier_ids.add(supplier_id)
            supplier_name = mapping.supplier.name if mapping.supplier else f'ID:{supplier_id}'
            stats['by_supplier'][supplier_name] = stats['by_supplier'].get(supplier_name, 0) + 1

        stats['total_suppliers'] = len(supplier_ids)
        return stats

    # ============================================================
    # 🔄 SYNC - مزامنة العلاقات
    # ============================================================

    def sync_mappings(self) -> Dict:
        """مزامنة العلاقات مع قمرة (تحديث بيانات المنتجات)"""
        mappings = ProductSupplierMapping.query.all()
        results = {'total': len(mappings), 'updated': 0, 'failed': 0, 'details': []}

        for mapping in mappings:
            product = self.client.get_product_by_qid(mapping.product_qid)
            if product:
                results['updated'] += 1
                results['details'].append({
                    'id': mapping.id,
                    'product_qid': mapping.product_qid,
                    'status': 'updated',
                    'message': 'المنتج موجود في قمرة'
                })
            else:
                results['failed'] += 1
                results['details'].append({
                    'id': mapping.id,
                    'product_qid': mapping.product_qid,
                    'status': 'failed',
                    'message': 'المنتج غير موجود في قمرة'
                })

        return results

    # ============================================================
    # 🗑️ CLEANUP - تنظيف العلاقات
    # ============================================================

    def cleanup_invalid_mappings(self) -> Dict:
        """حذف العلاقات غير الصالحة (منتجات غير موجودة في قمرة)"""
        mappings = ProductSupplierMapping.query.all()
        results = {'deleted': 0, 'details': []}

        for mapping in mappings:
            product = self.client.get_product_by_qid(mapping.product_qid)
            if not product:
                results['details'].append({
                    'id': mapping.id,
                    'product_qid': mapping.product_qid,
                    'message': 'المنتج غير موجود في قمرة'
                })
                db.session.delete(mapping)
                results['deleted'] += 1

        db.session.commit()
        return results

    # ============================================================
    # 🔍 SEARCH - البحث
    # ============================================================

    def search_by_supplier_name(self, supplier_name: str) -> List[Dict]:
        """البحث عن العلاقات حسب اسم المورد"""
        mappings = ProductSupplierMapping.query.join(Supplier).filter(
            Supplier.name.contains(supplier_name)
        ).all()

        return [{
            'id': m.id,
            'product_qid': m.product_qid,
            'supplier_id': m.supplier_id,
            'supplier_name': m.supplier.name if m.supplier else None,
            'status': m.status,
            'created_at': m.created_at.isoformat() if m.created_at else None
        } for m in mappings]

    def search_by_product_qid(self, product_qid: str) -> Dict:
        """البحث عن علاقة حسب QID"""
        return product_mapping.get_mapping_by_qid(product_qid)


# ============================================================
# 🚀 SINGLETON INSTANCE
# ============================================================

mapping_ops = ProductMappingOperations()
