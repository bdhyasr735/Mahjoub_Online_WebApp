# coding: utf-8
# 📂 apps/services/product_mapping_service.py

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from apps.extensions import db
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models import Supplier  # ✅ تم التصحيح
from .graphql_client import QomrahGraphQLClient


class ProductMappingService:
    """خدمة إدارة علاقات الربط بين المورد المحلي ومنتج قمرة"""

    def __init__(self):
        self.client = QomrahGraphQLClient()

    # ============================================================
    # 🔗 CRUD OPERATIONS - عمليات الربط الأساسية
    # ============================================================

    def add_mapping(self, product_qid: str, supplier_id: int,
                   status: str = 'active', internal_notes: str = None) -> Dict:
        """إضافة علاقة ربط جديدة"""
        try:
            supplier = Supplier.query.get(supplier_id)
            if not supplier:
                return {'success': False, 'message': f'المورد {supplier_id} غير موجود'}

            existing = ProductSupplierMapping.query.filter_by(product_qid=product_qid).first()
            if existing:
                return {'success': False, 'message': f'المنتج {product_qid} مرتبط بالفعل'}

            product = self.client.get_product_by_qid(product_qid)
            if not product:
                return {'success': False, 'message': f'المنتج {product_qid} غير موجود في قمرة'}

            mapping = ProductSupplierMapping(product_qid=product_qid, supplier_id=supplier_id, status=status)
            if internal_notes:
                mapping.internal_notes = internal_notes

            db.session.add(mapping)
            db.session.commit()

            return {
                'success': True,
                'message': 'تم إضافة الربط بنجاح',
                'data': {
                    'id': mapping.id,
                    'product_qid': mapping.product_qid,
                    'supplier_id': mapping.supplier_id,
                    'status': mapping.status,
                    'created_at': mapping.created_at.isoformat() if mapping.created_at else None
                }
            }

        except IntegrityError:
            db.session.rollback()
            return {'success': False, 'message': 'الربط موجود مسبقاً'}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': f'خطأ: {str(e)}'}

    def get_qid(self, supplier_id: int, status: str = 'active') -> List[str]:
        """استرجاع QIDs بناءً على معرف المورد"""
        mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id, status=status).all()
        return [m.product_qid for m in mappings]

    def get_mapping_by_qid(self, product_qid: str) -> Optional[Dict]:
        """استرجاع علاقة الربط بناءً على QID"""
        mapping = ProductSupplierMapping.query.filter_by(product_qid=product_qid).first()
        if not mapping:
            return None

        return {
            'id': mapping.id,
            'product_qid': mapping.product_qid,
            'supplier_id': mapping.supplier_id,
            'supplier_name': mapping.supplier.name if mapping.supplier else None,
            'status': mapping.status,
            'internal_notes': mapping.internal_notes,
            'created_at': mapping.created_at.isoformat() if mapping.created_at else None,
            'updated_at': mapping.updated_at.isoformat() if mapping.updated_at else None
        }

    def get_mappings_by_supplier(self, supplier_id: int) -> List[Dict]:
        """استرجاع جميع علاقات الربط لمورد معين"""
        mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id, status='active').all()
        return [{
            'id': m.id,
            'product_qid': m.product_qid,
            'supplier_id': m.supplier_id,
            'status': m.status,
            'created_at': m.created_at.isoformat() if m.created_at else None
        } for m in mappings]

    def get_supplier_by_qid(self, qid: str) -> Optional[int]:
        """جلب معرف المورد من خلال QID"""
        mapping = ProductSupplierMapping.query.filter_by(product_qid=qid, status='active').first()
        return mapping.supplier_id if mapping else None

    def update_mapping_status(self, product_qid: str, status: str) -> Dict:
        """تحديث حالة الربط"""
        mapping = ProductSupplierMapping.query.filter_by(product_qid=product_qid).first()
        if not mapping:
            return {'success': False, 'message': f'الربط غير موجود للمنتج {product_qid}'}

        mapping.status = status
        mapping.updated_at = datetime.utcnow()
        db.session.commit()

        return {'success': True, 'message': f'تم تحديث حالة الربط إلى {status}'}

    def delete_mapping(self, product_qid: str) -> Dict:
        """حذف علاقة ربط"""
        mapping = ProductSupplierMapping.query.filter_by(product_qid=product_qid).first()
        if not mapping:
            return {'success': False, 'message': f'الربط غير موجود للمنتج {product_qid}'}

        db.session.delete(mapping)
        db.session.commit()

        return {'success': True, 'message': 'تم حذف الربط بنجاح'}

    def get_all_mappings(self) -> Dict[str, Dict]:
        """جلب جميع العلاقات النشطة"""
        mappings = ProductSupplierMapping.query.filter_by(status='active').all()
        result = {}
        for mapping in mappings:
            result[f"mapping_{mapping.id}"] = {
                'id': mapping.id,
                'qid': mapping.product_qid,
                'supplier_id': mapping.supplier_id,
                'supplier_name': mapping.supplier.name if mapping.supplier else None,
                'status': mapping.status,
                'created_at': mapping.created_at.isoformat() if mapping.created_at else None
            }
        return result


# ============================================================
# 🚀 SINGLETON INSTANCE
# ============================================================

product_mapping = ProductMappingService()
