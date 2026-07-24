# coding: utf-8
# 📂 apps/services/product_mapping_service.py

from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from apps.extensions import db
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier import Supplier
from .graphql_client import QomrahGraphQLClient


class ProductMappingService:
    """
    خدمة إدارة علاقات الربط بين المورد المحلي ومنتج قمرة
    باستخدام قاعدة البيانات (SQLAlchemy)
    """
    
    def __init__(self):
        self.client = QomrahGraphQLClient()
    
    # ============================================================
    # 🔗 MAPPING OPERATIONS - عمليات الربط
    # ============================================================
    
    def add_mapping(self, product_qid: str, supplier_id: int,
                   status: str = 'active', internal_notes: str = None) -> Dict:
        """
        إضافة علاقة ربط جديدة في قاعدة البيانات
        
        Args:
            product_qid: معرف المنتج في قمرة
            supplier_id: معرف المورد في النظام المحلي
            status: حالة الربط (active, inactive, pending)
            internal_notes: ملاحظات إدارية (مشفر)
        
        Returns:
            Dict: {success: bool, message: str, data: dict}
        """
        try:
            # التحقق من وجود المورد
            supplier = Supplier.query.get(supplier_id)
            if not supplier:
                return {
                    'success': False,
                    'message': f'المورد {supplier_id} غير موجود',
                    'data': None
                }
            
            # التحقق من عدم وجود ربط مكرر
            existing = ProductSupplierMapping.query.filter_by(
                product_qid=product_qid
            ).first()
            if existing:
                return {
                    'success': False,
                    'message': f'المنتج {product_qid} مرتبط بالفعل بالمورد {existing.supplier_id}',
                    'data': None
                }
            
            # التحقق من وجود المنتج في قمرة
            product = self.client.get_product_by_qid(product_qid)
            if not product:
                return {
                    'success': False,
                    'message': f'المنتج {product_qid} غير موجود في قمرة',
                    'data': None
                }
            
            # إنشاء الربط
            mapping = ProductSupplierMapping(
                product_qid=product_qid,
                supplier_id=supplier_id,
                status=status
            )
            
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
            return {
                'success': False,
                'message': 'الربط موجود مسبقاً',
                'data': None
            }
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'خطأ: {str(e)}',
                'data': None
            }
    
    def get_qid(self, supplier_id: int, status: str = 'active') -> List[str]:
        """
        استرجاع QIDs بناءً على معرف المورد المحلي
        
        Args:
            supplier_id: معرف المورد في النظام المحلي
            status: حالة الربط (active, inactive, pending)
        
        Returns:
            List[str]: قائمة QIDs المنتجات في قمرة
        """
        mappings = ProductSupplierMapping.query.filter_by(
            supplier_id=supplier_id,
            status=status
        ).all()
        
        return [m.product_qid for m in mappings]
    
    def get_mapping_by_qid(self, product_qid: str) -> Optional[Dict]:
        """
        استرجاع علاقة الربط بناءً على QID
        
        Args:
            product_qid: معرف المنتج في قمرة
        
        Returns:
            Dict: بيانات الربط أو None
        """
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=product_qid
        ).first()
        
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
        """
        استرجاع جميع علاقات الربط لمورد معين
        
        Args:
            supplier_id: معرف المورد في النظام المحلي
        
        Returns:
            List[Dict]: قائمة العلاقات
        """
        mappings = ProductSupplierMapping.query.filter_by(
            supplier_id=supplier_id,
            status='active'
        ).all()
        
        return [{
            'id': m.id,
            'product_qid': m.product_qid,
            'supplier_id': m.supplier_id,
            'status': m.status,
            'created_at': m.created_at.isoformat() if m.created_at else None,
            'updated_at': m.updated_at.isoformat() if m.updated_at else None
        } for m in mappings]
    
    def get_supplier_by_qid(self, qid: str) -> Optional[int]:
        """
        جلب معرف المورد من خلال QID
        
        Args:
            qid: معرف المنتج في قمرة
        
        Returns:
            int: معرف المورد أو None
        """
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=qid,
            status='active'
        ).first()
        return mapping.supplier_id if mapping else None
    
    def update_mapping_status(self, product_qid: str, status: str) -> Dict:
        """
        تحديث حالة الربط
        
        Args:
            product_qid: معرف المنتج في قمرة
            status: الحالة الجديدة (active, inactive, pending)
        
        Returns:
            Dict: {success: bool, message: str}
        """
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=product_qid
        ).first()
        
        if not mapping:
            return {
                'success': False,
                'message': f'الربط غير موجود للمنتج {product_qid}'
            }
        
        mapping.status = status
        mapping.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {
            'success': True,
            'message': f'تم تحديث حالة الربط إلى {status}'
        }
    
    def update_internal_notes(self, product_qid: str, notes: str) -> Dict:
        """
        تحديث الملاحظات الداخلية (مشفر)
        
        Args:
            product_qid: معرف المنتج في قمرة
            notes: الملاحظات الجديدة
        
        Returns:
            Dict: {success: bool, message: str}
        """
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=product_qid
        ).first()
        
        if not mapping:
            return {
                'success': False,
                'message': f'الربط غير موجود للمنتج {product_qid}'
            }
        
        mapping.internal_notes = notes
        mapping.updated_at = datetime.utcnow()
        db.session.commit()
        
        return {
            'success': True,
            'message': 'تم تحديث الملاحظات بنجاح'
        }
    
    def delete_mapping(self, product_qid: str) -> Dict:
        """
        حذف علاقة ربط
        
        Args:
            product_qid: معرف المنتج في قمرة
        
        Returns:
            Dict: {success: bool, message: str}
        """
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=product_qid
        ).first()
        
        if not mapping:
            return {
                'success': False,
                'message': f'الربط غير موجود للمنتج {product_qid}'
            }
        
        db.session.delete(mapping)
        db.session.commit()
        
        return {
            'success': True,
            'message': 'تم حذف الربط بنجاح'
        }
    
    # ============================================================
    # 🔍 VERIFICATION - التحقق من العلاقات
    # ============================================================
    
    def verify_mapping(self, product_qid: str) -> Dict:
        """
        التحقق من صحة العلاقة (وجود المنتج في قمرة)
        
        Args:
            product_qid: معرف المنتج في قمرة
        
        Returns:
            Dict: {valid: bool, product: dict, message: str}
        """
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=product_qid
        ).first()
        
        if not mapping:
            return {
                'valid': False,
                'product': None,
                'message': f'الربط غير موجود للمنتج {product_qid}'
            }
        
        product = self.client.get_product_by_qid(product_qid)
        
        if product:
            return {
                'valid': True,
                'product': product,
                'message': 'المنتج موجود في قمرة'
            }
        else:
            return {
                'valid': False,
                'product': None,
                'message': f'المنتج {product_qid} غير موجود في قمرة'
            }
    
    def verify_all_mappings(self) -> Dict:
        """
        التحقق من جميع العلاقات
        
        Returns:
            Dict: {total: int, valid: int, invalid: int, details: List}
        """
        mappings = ProductSupplierMapping.query.all()
        
        results = {
            'total': len(mappings),
            'valid': 0,
            'invalid': 0,
            'details': []
        }
        
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
        """
        الحصول على إحصائيات العلاقات
        
        Returns:
            Dict: {total, by_status, by_supplier, total_suppliers}
        """
        mappings = ProductSupplierMapping.query.all()
        
        stats = {
            'total': len(mappings),
            'by_status': {},
            'by_supplier': {},
            'total_suppliers': 0
        }
        
        supplier_ids = set()
        
        for mapping in mappings:
            # حسب الحالة
            status = mapping.status
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # حسب المورد
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
        """
        مزامنة العلاقات مع قمرة (تحديث بيانات المنتجات)
        
        Returns:
            Dict: {total: int, updated: int, failed: int, details: List}
        """
        mappings = ProductSupplierMapping.query.all()
        
        results = {
            'total': len(mappings),
            'updated': 0,
            'failed': 0,
            'details': []
        }
        
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
                    'message': f'المنتج غير موجود في قمرة'
                })
        
        return results
    
    # ============================================================
    # 🗑️ CLEANUP - تنظيف العلاقات
    # ============================================================
    
    def cleanup_invalid_mappings(self) -> Dict:
        """
        حذف العلاقات غير الصالحة (منتجات غير موجودة في قمرة)
        
        Returns:
            Dict: {deleted: int, details: List}
        """
        mappings = ProductSupplierMapping.query.all()
        
        results = {
            'deleted': 0,
            'details': []
        }
        
        for mapping in mappings:
            product = self.client.get_product_by_qid(mapping.product_qid)
            
            if not product:
                results['details'].append({
                    'id': mapping.id,
                    'product_qid': mapping.product_qid,
                    'message': f'المنتج غير موجود في قمرة'
                })
                db.session.delete(mapping)
                results['deleted'] += 1
        
        db.session.commit()
        return results
    
    # ============================================================
    # 🔍 SEARCH - البحث
    # ============================================================
    
    def search_by_supplier_name(self, supplier_name: str) -> List[Dict]:
        """
        البحث عن العلاقات حسب اسم المورد
        
        Args:
            supplier_name: اسم المورد (جزئي)
        
        Returns:
            List[Dict]: قائمة العلاقات
        """
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
    
    def search_by_product_qid(self, product_qid: str) -> Optional[Dict]:
        """
        البحث عن علاقة حسب QID
        
        Args:
            product_qid: معرف المنتج في قمرة
        
        Returns:
            Dict: بيانات العلاقة
        """
        return self.get_mapping_by_qid(product_qid)
    
    def get_all_mappings(self) -> Dict[str, Dict]:
        """
        جلب جميع العلاقات
        
        Returns:
            Dict: جميع العلاقات {local_id: mapping_data}
        """
        mappings = ProductSupplierMapping.query.filter_by(status='active').all()
        
        result = {}
        for mapping in mappings:
            result[f"mapping_{mapping.id}"] = {
                'id': mapping.id,
                'qid': mapping.product_qid,
                'supplier_id': mapping.supplier_id,
                'supplier_name': mapping.supplier.name if mapping.supplier else None,
                'product_title': None,  # سيتم ملؤه لاحقاً
                'product_status': None,  # سيتم ملؤه لاحقاً
                'status': mapping.status,
                'created_at': mapping.created_at.isoformat() if mapping.created_at else None,
                'updated_at': mapping.updated_at.isoformat() if mapping.updated_at else None
            }
        
        return result


# ============================================================
# 🚀 SINGLETON INSTANCE
# ============================================================

product_mapping = ProductMappingService()


# ============================================================
# 📋 EXPORTS
# ============================================================

__all__ = [
    'ProductMappingService',
    'product_mapping'
]
