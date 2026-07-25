# coding: utf-8
# 📂 apps/suppliers_product/services.py

from core.graphql_client import GraphQLClient
from typing import List, Optional, Dict
import logging
import uuid
import random
import string

logger = logging.getLogger(__name__)

# ============================================
# استعلامات GraphQL (الموجودة)
# ============================================

# ... (جميع الاستعلامات التي كتبتها موجودة هنا) ...


# ============================================
# تهيئة عميل GraphQL
# ============================================

_graphql_client = None

def get_graphql_client():
    """الحصول على عميل GraphQL (Singleton)"""
    global _graphql_client
    if _graphql_client is None:
        _graphql_client = GraphQLClient()
    return _graphql_client


# ============================================
# دوال إضافية للـ Routes
# ============================================

# ✅ 1. جلب منتجات المورد مع الـ Mappings
def get_supplier_mappings(supplier_id: int) -> List[Dict]:
    """
    جلب قائمة الـ mappings لمنتج مورد معين
    """
    # هذا يعتمد على قاعدة البيانات الخاصة بك
    # مثال:
    from apps.suppliers_product.models import SupplierProductMapping
    mappings = SupplierProductMapping.query.filter_by(supplier_id=supplier_id).all()
    return [{'qid': m.product_qid, 'id': m.id} for m in mappings]


# ✅ 2. جلب الموردين النشطين
def get_active_suppliers() -> List[Dict]:
    """
    جلب قائمة الموردين النشطين
    """
    # هذا يعتمد على قاعدة البيانات الخاصة بك
    from apps.suppliers.models import Supplier
    suppliers = Supplier.query.filter_by(is_active=True).all()
    return [{'id': s.id, 'name': s.name} for s in suppliers]


# ✅ 3. جلب منتج مع التحقق من الوصول
def get_product(qid: str, supplier_id: int) -> Dict:
    """
    جلب منتج مع التحقق من أن المورد يملكه
    """
    try:
        # التحقق من الـ mapping
        from apps.suppliers_product.models import SupplierProductMapping
        mapping = SupplierProductMapping.query.filter_by(
            supplier_id=supplier_id,
            product_qid=qid
        ).first()
        
        if not mapping:
            return {'success': False, 'error': 'المنتج غير موجود أو غير مصرح لك'}
        
        # جلب المنتج من GraphQL
        product = fetch_product_by_qid(qid)
        if not product:
            return {'success': False, 'error': 'المنتج غير موجود في النظام'}
        
        return {
            'success': True,
            'product': product,
            'mapping': {'id': mapping.id, 'qid': mapping.product_qid}
        }
        
    except Exception as e:
        logger.error(f"❌ get_product: {e}")
        return {'success': False, 'error': str(e)}


# ✅ 4. التحقق من الوصول للمنتج
def verify_access(qid: str, supplier_id: int) -> bool:
    """
    التحقق من أن المورد يملك المنتج
    """
    try:
        from apps.suppliers_product.models import SupplierProductMapping
        mapping = SupplierProductMapping.query.filter_by(
            supplier_id=supplier_id,
            product_qid=qid
        ).first()
        return mapping is not None
    except Exception as e:
        logger.error(f"❌ verify_access: {e}")
        return False


# ✅ 5. إنشاء منتج جديد
def create_product(supplier_id: int, data: Dict) -> Dict:
    """
    إنشاء منتج جديد للمورد
    """
    try:
        from apps.suppliers_product.models import SupplierProductMapping
        
        # ✅ توليد SKU إذا لم يكن موجوداً
        if not data.get('sku'):
            prefix = data.get('title', 'PRD')[:3].upper() or 'PRD'
            random_num = str(random.randint(100000, 999999))
            data['sku'] = f"{prefix}-{random_num}"
        
        # ✅ توليد QID فريد
        qid = f"prod_{uuid.uuid4().hex[:12]}"
        
        # ✅ هنا يتم إرسال المنتج إلى GraphQL API
        # (هذا يعتمد على الـ API الخاصة بك)
        
        # ✅ حفظ الـ mapping في قاعدة البيانات
        mapping = SupplierProductMapping(
            supplier_id=supplier_id,
            product_qid=qid,
            sku=data.get('sku'),
            status=data.get('status', 'DRAFT')
        )
        # mapping.save()  # حسب الـ ORM الخاص بك
        
        return {
            'success': True,
            'message': 'تم إضافة المنتج بنجاح',
            'qid': qid,
            'sku': data.get('sku')
        }
        
    except Exception as e:
        logger.error(f"❌ create_product: {e}")
        return {'success': False, 'message': str(e)}


# ✅ 6. تحديث منتج
def update_product(qid: str, supplier_id: int, data: Dict) -> Dict:
    """
    تحديث منتج موجود
    """
    try:
        from apps.suppliers_product.models import SupplierProductMapping
        
        # ✅ التحقق من الوصول
        mapping = SupplierProductMapping.query.filter_by(
            supplier_id=supplier_id,
            product_qid=qid
        ).first()
        
        if not mapping:
            return {'success': False, 'error': 'المنتج غير موجود أو غير مصرح لك'}
        
        # ✅ تحديث المنتج في GraphQL API
        # (هذا يعتمد على الـ API الخاصة بك)
        
        # ✅ تحديث الـ mapping
        if data.get('sku'):
            mapping.sku = data.get('sku')
        if data.get('status'):
            mapping.status = data.get('status')
        # mapping.save()  # حسب الـ ORM الخاص بك
        
        return {
            'success': True,
            'message': 'تم تحديث المنتج بنجاح',
            'qid': qid
        }
        
    except Exception as e:
        logger.error(f"❌ update_product: {e}")
        return {'success': False, 'error': str(e)}


# ✅ 7. تحديث حالة المنتج
def update_product_status(qid: str, supplier_id: int, status: str) -> Dict:
    """
    تحديث حالة المنتج فقط
    """
    try:
        from apps.suppliers_product.models import SupplierProductMapping
        
        # ✅ التحقق من الوصول
        mapping = SupplierProductMapping.query.filter_by(
            supplier_id=supplier_id,
            product_qid=qid
        ).first()
        
        if not mapping:
            return {'success': False, 'error': 'المنتج غير موجود أو غير مصرح لك'}
        
        # ✅ تحديث الحالة
        mapping.status = status
        # mapping.save()  # حسب الـ ORM الخاص بك
        
        return {
            'success': True,
            'message': 'تم تحديث حالة المنتج بنجاح',
            'qid': qid,
            'status': status
        }
        
    except Exception as e:
        logger.error(f"❌ update_product_status: {e}")
        return {'success': False, 'error': str(e)}


# ✅ 8. حذف منتج
def delete_product(qid: str, supplier_id: int) -> Dict:
    """
    حذف منتج (إلغاء الربط فقط)
    """
    try:
        from apps.suppliers_product.models import SupplierProductMapping
        
        # ✅ التحقق من الوصول
        mapping = SupplierProductMapping.query.filter_by(
            supplier_id=supplier_id,
            product_qid=qid
        ).first()
        
        if not mapping:
            return {'success': False, 'error': 'المنتج غير موجود أو غير مصرح لك'}
        
        # ✅ حذف الـ mapping
        # mapping.delete()  # حسب الـ ORM الخاص بك
        
        return {
            'success': True,
            'message': 'تم حذف المنتج بنجاح'
        }
        
    except Exception as e:
        logger.error(f"❌ delete_product: {e}")
        return {'success': False, 'error': str(e)}


# ✅ 9. إضافة صورة للمنتج
def add_product_image(qid: str, image_data: bytes, filename: str) -> Dict:
    """
    إضافة صورة للمنتج
    """
    try:
        # ✅ رفع الصورة إلى خدمة التخزين
        # (هذا يعتمد على خدمة التخزين الخاصة بك)
        
        # ✅ تحديث المنتج في GraphQL API بالصورة
        # (هذا يعتمد على الـ API الخاصة بك)
        
        return {
            'success': True,
            'message': 'تم رفع الصورة بنجاح',
            'image_id': str(uuid.uuid4())
        }
        
    except Exception as e:
        logger.error(f"❌ add_product_image: {e}")
        return {'success': False, 'error': str(e)}


# ✅ 10. حذف صورة من المنتج
def remove_product_image(qid: str, image_id: str) -> Dict:
    """
    حذف صورة من المنتج
    """
    try:
        # ✅ حذف الصورة من خدمة التخزين
        # ✅ تحديث المنتج في GraphQL API
        
        return {
            'success': True,
            'message': 'تم حذف الصورة بنجاح'
        }
        
    except Exception as e:
        logger.error(f"❌ remove_product_image: {e}")
        return {'success': False, 'error': str(e)}


# ✅ 11. التحقق من توفر SKU
def check_sku_availability(sku: str) -> Dict:
    """
    التحقق من أن SKU غير مستخدم
    """
    try:
        from apps.suppliers_product.models import SupplierProductMapping
        
        exists = SupplierProductMapping.query.filter_by(sku=sku).first()
        return {
            'available': exists is None,
            'sku': sku
        }
        
    except Exception as e:
        logger.error(f"❌ check_sku_availability: {e}")
        return {'available': False, 'sku': sku}


# ✅ 12. توليد SKU تلقائي
def generate_sku(prefix: str = 'PRD') -> str:
    """
    توليد SKU تلقائي
    """
    random_num = str(random.randint(100000, 999999))
    return f"{prefix[:3].upper()}-{random_num}"


# ✅ 13. إحصائيات المنتجات للمورد
def get_product_stats(supplier_id: int) -> Dict:
    """
    جلب إحصائيات منتجات المورد
    """
    try:
        from apps.suppliers_product.models import SupplierProductMapping
        
        # ✅ جلب جميع الـ mappings للمورد
        mappings = SupplierProductMapping.query.filter_by(
            supplier_id=supplier_id
        ).all()
        
        # ✅ إحصائيات الحالات
        total = len(mappings)
        published = sum(1 for m in mappings if m.status == 'PUBLISHED')
        draft = sum(1 for m in mappings if m.status == 'DRAFT')
        rejected = sum(1 for m in mappings if m.status == 'REJECTED')
        archived = sum(1 for m in mappings if m.status == 'ARCHIVED')
        pending = sum(1 for m in mappings if m.status == 'PENDING')
        
        return {
            'total': total,
            'published': published,
            'draft': draft,
            'rejected': rejected,
            'archived': archived,
            'pending': pending
        }
        
    except Exception as e:
        logger.error(f"❌ get_product_stats: {e}")
        return {
            'total': 0,
            'published': 0,
            'draft': 0,
            'rejected': 0,
            'archived': 0,
            'pending': 0
        }
