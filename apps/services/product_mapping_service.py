# coding: utf-8
# 📂 apps/services/product_mapping_service.py

from typing import Dict, List, Optional, Any
from .graphql_client import QomrahGraphQLClient
import json
import os
from datetime import datetime


class ProductMappingService:
    """
    خدمة إدارة علاقات الربط بين المورد المحلي ومنتج قمرة
    
    التخزين المحلي:
    - معرف المورد (Supplier ID / Local ID)
    - معرف المنتج في قمرة (QID)
    - بيانات إضافية: تاريخ الإنشاء، آخر تحديث، الحالة
    """
    
    def __init__(self, storage_file: str = None):
        self.client = QomrahGraphQLClient()
        
        # تحديد ملف التخزين
        if storage_file is None:
            # استخدام مجلد البيانات
            data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
            os.makedirs(data_dir, exist_ok=True)
            storage_file = os.path.join(data_dir, 'product_mappings.json')
        
        self.storage_file = storage_file
        self._mappings = None
        self._load_mappings()
    
    # ============================================================
    # 💾 STORAGE - التخزين المحلي
    # ============================================================
    
    def _load_mappings(self):
        """تحميل العلاقات من ملف التخزين"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self._mappings = json.load(f)
                print(f"✅ تم تحميل {len(self._mappings)} علاقة من الملف")
            except Exception as e:
                print(f"⚠️ خطأ في تحميل الملف: {e}")
                self._mappings = {}
        else:
            self._mappings = {}
            self._save_mappings()
    
    def _save_mappings(self):
        """حفظ العلاقات في ملف التخزين"""
        try:
            os.makedirs(os.path.dirname(self.storage_file), exist_ok=True)
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self._mappings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ خطأ في حفظ الملف: {e}")
            return False
    
    # ============================================================
    # 🔗 MAPPING OPERATIONS - عمليات الربط
    # ============================================================
    
    def add_mapping(self, local_id: str, qid: str, 
                   supplier_name: str = None, metadata: Dict = None) -> bool:
        """
        إضافة علاقة ربط جديدة
        
        Args:
            local_id: معرف المورد في النظام المحلي
            qid: معرف المنتج في قمرة
            supplier_name: اسم المورد (اختياري)
            metadata: بيانات إضافية (اختياري)
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        if local_id in self._mappings:
            print(f"⚠️ العلاقة موجودة بالفعل للمورد {local_id}")
            return False
        
        # التحقق من وجود المنتج في قمرة
        product = self.client.get_product_by_qid(qid)
        if not product:
            print(f"❌ المنتج {qid} غير موجود في قمرة")
            return False
        
        # إضافة العلاقة
        self._mappings[local_id] = {
            'qid': qid,
            'supplier_name': supplier_name,
            'product_title': product.get('title'),
            'product_status': product.get('status'),
            'metadata': metadata or {},
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }
        
        return self._save_mappings()
    
    def get_qid(self, local_id: str) -> Optional[str]:
        """
        استرجاع QID بناءً على معرف المورد المحلي
        
        Args:
            local_id: معرف المورد في النظام المحلي
        
        Returns:
            str: QID المنتج في قمرة أو None
        """
        mapping = self._mappings.get(local_id)
        return mapping.get('qid') if mapping else None
    
    def get_mapping(self, local_id: str) -> Optional[Dict]:
        """
        استرجاع العلاقة الكاملة لمورد
        
        Args:
            local_id: معرف المورد في النظام المحلي
        
        Returns:
            Dict: بيانات العلاقة أو None
        """
        return self._mappings.get(local_id)
    
    def get_local_id(self, qid: str) -> Optional[str]:
        """
        استرجاع معرف المورد المحلي بناءً على QID
        
        Args:
            qid: معرف المنتج في قمرة
        
        Returns:
            str: معرف المورد المحلي أو None
        """
        for local_id, mapping in self._mappings.items():
            if mapping.get('qid') == qid:
                return local_id
        return None
    
    def update_mapping(self, local_id: str, 
                      qid: str = None, 
                      supplier_name: str = None,
                      metadata: Dict = None) -> bool:
        """
        تحديث علاقة ربط موجودة
        
        Args:
            local_id: معرف المورد في النظام المحلي
            qid: معرف المنتج الجديد في قمرة (اختياري)
            supplier_name: اسم المورد الجديد (اختياري)
            metadata: بيانات إضافية جديدة (اختياري)
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        if local_id not in self._mappings:
            print(f"❌ العلاقة غير موجودة للمورد {local_id}")
            return False
        
        mapping = self._mappings[local_id]
        
        if qid is not None:
            # التحقق من وجود المنتج في قمرة
            product = self.client.get_product_by_qid(qid)
            if not product:
                print(f"❌ المنتج {qid} غير موجود في قمرة")
                return False
            mapping['qid'] = qid
            mapping['product_title'] = product.get('title')
            mapping['product_status'] = product.get('status')
        
        if supplier_name is not None:
            mapping['supplier_name'] = supplier_name
        
        if metadata is not None:
            mapping['metadata'].update(metadata)
        
        mapping['updated_at'] = datetime.now().isoformat()
        
        return self._save_mappings()
    
    def delete_mapping(self, local_id: str) -> bool:
        """
        حذف علاقة ربط
        
        Args:
            local_id: معرف المورد في النظام المحلي
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        if local_id not in self._mappings:
            print(f"❌ العلاقة غير موجودة للمورد {local_id}")
            return False
        
        del self._mappings[local_id]
        return self._save_mappings()
    
    # ============================================================
    # 🔍 VERIFICATION - التحقق من العلاقات
    # ============================================================
    
    def verify_mapping(self, local_id: str) -> Dict:
        """
        التحقق من صحة العلاقة (وجود المنتج في قمرة)
        
        Args:
            local_id: معرف المورد في النظام المحلي
        
        Returns:
            Dict: {valid: bool, product: dict, message: str}
        """
        mapping = self._mappings.get(local_id)
        if not mapping:
            return {
                'valid': False,
                'product': None,
                'message': f'العلاقة غير موجودة للمورد {local_id}'
            }
        
        qid = mapping.get('qid')
        product = self.client.get_product_by_qid(qid)
        
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
                'message': f'المنتج {qid} غير موجود في قمرة'
            }
    
    def verify_all_mappings(self) -> Dict:
        """
        التحقق من جميع العلاقات
        
        Returns:
            Dict: {total: int, valid: int, invalid: int, details: List}
        """
        results = {
            'total': len(self._mappings),
            'valid': 0,
            'invalid': 0,
            'details': []
        }
        
        for local_id in self._mappings:
            result = self.verify_mapping(local_id)
            results['details'].append({
                'local_id': local_id,
                'valid': result['valid'],
                'message': result['message']
            })
            if result['valid']:
                results['valid'] += 1
            else:
                results['invalid'] += 1
        
        return results
    
    # ============================================================
    # 📊 GET ALL MAPPINGS - جلب جميع العلاقات
    # ============================================================
    
    def get_all_mappings(self) -> Dict[str, Dict]:
        """
        جلب جميع العلاقات
        
        Returns:
            Dict: جميع العلاقات {local_id: mapping_data}
        """
        return self._mappings
    
    def get_mappings_by_supplier(self, supplier_name: str) -> List[Dict]:
        """
        جلب العلاقات حسب اسم المورد
        
        Args:
            supplier_name: اسم المورد
        
        Returns:
            List[Dict]: قائمة العلاقات
        """
        results = []
        for local_id, mapping in self._mappings.items():
            if mapping.get('supplier_name') == supplier_name:
                results.append({
                    'local_id': local_id,
                    **mapping
                })
        return results
    
    def get_mappings_by_status(self, status: str) -> List[Dict]:
        """
        جلب العلاقات حسب حالة المنتج
        
        Args:
            status: حالة المنتج (ACTIVE, INACTIVE, DRAFT, ARCHIVED)
        
        Returns:
            List[Dict]: قائمة العلاقات
        """
        results = []
        for local_id, mapping in self._mappings.items():
            if mapping.get('product_status') == status:
                results.append({
                    'local_id': local_id,
                    **mapping
                })
        return results
    
    def get_stats(self) -> Dict:
        """
        الحصول على إحصائيات العلاقات
        
        Returns:
            Dict: {total, by_supplier, by_status, created_today}
        """
        stats = {
            'total': len(self._mappings),
            'by_supplier': {},
            'by_status': {},
            'created_today': 0
        }
        
        today = datetime.now().date().isoformat()
        
        for mapping in self._mappings.values():
            # حسب المورد
            supplier = mapping.get('supplier_name', 'unknown')
            stats['by_supplier'][supplier] = stats['by_supplier'].get(supplier, 0) + 1
            
            # حسب الحالة
            status = mapping.get('product_status', 'unknown')
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            
            # تم إنشاؤها اليوم
            created_at = mapping.get('created_at', '')
            if created_at.startswith(today):
                stats['created_today'] += 1
        
        return stats
    
    # ============================================================
    # 🔄 SYNC OPERATIONS - مزامنة العلاقات
    # ============================================================
    
    def sync_mappings(self) -> Dict:
        """
        مزامنة العلاقات مع قمرة (تحديث بيانات المنتجات)
        
        Returns:
            Dict: {total: int, updated: int, failed: int, details: List}
        """
        results = {
            'total': len(self._mappings),
            'updated': 0,
            'failed': 0,
            'details': []
        }
        
        for local_id, mapping in self._mappings.items():
            qid = mapping.get('qid')
            product = self.client.get_product_by_qid(qid)
            
            if product:
                mapping['product_title'] = product.get('title')
                mapping['product_status'] = product.get('status')
                mapping['updated_at'] = datetime.now().isoformat()
                results['updated'] += 1
                results['details'].append({
                    'local_id': local_id,
                    'status': 'updated',
                    'message': 'تم التحديث'
                })
            else:
                results['failed'] += 1
                results['details'].append({
                    'local_id': local_id,
                    'status': 'failed',
                    'message': f'المنتج {qid} غير موجود'
                })
        
        self._save_mappings()
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
        results = {
            'deleted': 0,
            'details': []
        }
        
        to_delete = []
        for local_id in self._mappings:
            result = self.verify_mapping(local_id)
            if not result['valid']:
                to_delete.append(local_id)
                results['details'].append({
                    'local_id': local_id,
                    'message': result['message']
                })
        
        for local_id in to_delete:
            del self._mappings[local_id]
            results['deleted'] += 1
        
        self._save_mappings()
        return results


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


# ============================================================
# 🧪 TEST - اختبار سريع
# ============================================================

if __name__ == "__main__":
    service = ProductMappingService()
    
    # ✅ مثال: إضافة علاقة جديدة
    # service.add_mapping(
    #     local_id="SUP-001",
    #     qid="qmr_123456",
    #     supplier_name="المورد الأول",
    #     metadata={"category": "electronics", "priority": 1}
    # )
    
    # ✅ مثال: استرجاع QID
    # qid = service.get_qid("SUP-001")
    # print(f"QID: {qid}")
    
    # ✅ مثال: إحصائيات
    stats = service.get_stats()
    print(f"📊 الإحصائيات: {stats}")
    
    print("✅ Product Mapping Service ready!")
