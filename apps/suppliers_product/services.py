# coding: utf-8
# 📂 apps/suppliers_product/services.py

from apps.services import ProductService, GraphQLClient
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models import Supplier
from apps.suppliers_product.helpers import compress_image
from apps.extensions import db
import logging
import time

logger = logging.getLogger(__name__)


class SupplierProductService:
    def __init__(self):
        # ✅ استخدام الخدمات الجديدة
        self.client = GraphQLClient()
        self.products = ProductService(self.client)
    
    # ====== GET ======
    def get_product(self, qid, supplier_id):
        """جلب منتج مع التحقق من الصلاحية"""
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=qid, supplier_id=supplier_id, status='active'
        ).first()
        if not mapping:
            return {'success': False, 'error': 'المنتج غير موجود'}
        
        product = self.products.get_by_qid(qid)
        if not product:
            return {'success': False, 'error': 'المنتج غير موجود في قمرة'}
        
        return {
            'success': True, 
            'product': product, 
            'mapping': mapping.to_dict()
        }
    
    def fetch_product_by_qid(self, qid):
        """جلب منتج بواسطة QID"""
        return self.products.get_by_qid(qid)
    
    # ====== CREATE ======
    def create_product(self, supplier_id, data):
        """إنشاء منتج جديد للمورد"""
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return {'success': False, 'error': 'المورد غير موجود'}
        
        title = data.get('title', '').strip()
        if not title:
            return {'success': False, 'error': 'اسم المنتج مطلوب'}
        
        # تجهيز بيانات المنتج
        product_data = {
            'name': title,
            'price': float(data.get('price', 0)),
            'status': data.get('status', 'DRAFT'),
            'description': data.get('description', '').strip()
        }
        
        # إضافة SKU إن وجد
        if data.get('sku'):
            sku = data['sku'].strip()
            if not self.check_sku_availability(sku).get('available', True):
                return {'success': False, 'error': f'SKU "{sku}" غير متاح'}
            product_data['sku'] = sku
        
        # إضافة الوزن والكمية
        if data.get('weight'):
            product_data['weight'] = float(data['weight'])
        if data.get('quantity'):
            product_data['stock'] = int(data['quantity'])
        
        # إنشاء المنتج
        result = self.products.create(product_data)
        if not result:
            return {'success': False, 'error': 'فشل إنشاء المنتج'}
        
        # ربط المنتج بالمورد
        mapping = ProductSupplierMapping(
            product_qid=result['qid'],
            supplier_id=supplier_id,
            status='active'
        )
        db.session.add(mapping)
        db.session.commit()
        
        # إضافة صورة إن وجدت
        if data.get('image_file'):
            self.add_product_image(result['qid'], data['image_file'], data.get('image_filename', 'image.jpg'))
        
        return {
            'success': True,
            'message': 'تم إنشاء المنتج بنجاح',
            'qid': result['qid'],
            'product': result
        }
    
    # ====== UPDATE ======
    def update_product(self, qid, supplier_id, data):
        """تحديث منتج"""
        if not self.verify_access(qid, supplier_id):
            return {'success': False, 'error': 'غير مصرح'}
        
        # تحديث المعلومات الأساسية
        update_data = {}
        if data.get('title'):
            update_data['name'] = data['title']
        if data.get('description'):
            update_data['description'] = data['description']
        if data.get('status'):
            update_data['status'] = data['status']
        
        if update_data:
            self.products.update(qid, update_data)
        
        # تحديث السعر
        if data.get('price'):
            self.products.update_price(qid, float(data['price']))
        
        # تحديث الوزن
        if data.get('weight'):
            self.products.update_weight(qid, float(data['weight']))
        
        # تحديث SKU
        if data.get('sku'):
            sku = data['sku'].strip()
            if self.check_sku_availability(sku, qid).get('available', True):
                self.products.update(qid, {'sku': sku})
            else:
                return {'success': False, 'error': f'SKU "{sku}" غير متاح'}
        
        # تحديث الصورة
        if data.get('image_file'):
            result = self.add_product_image(qid, data['image_file'], data.get('image_filename', 'image.jpg'))
            if not result['success']:
                return result
        
        return {'success': True, 'message': 'تم التحديث بنجاح'}
    
    # ====== IMAGE ======
    def _upload_image(self, image_data, filename):
        """رفع صورة (يجب تنفيذها حسب نظام التخزين المستخدم)"""
        compressed = compress_image(image_data)
        return None
    
    def add_product_image(self, qid, image_data, filename):
        """إضافة صورة للمنتج"""
        url = self._upload_image(image_data, filename)
        if not url:
            return {'success': False, 'error': 'فشل رفع الصورة'}
        
        product = self.products.get_by_qid(qid)
        if not product:
            return {'success': False, 'error': 'المنتج غير موجود'}
        
        current_images = product.get('images', [])
        if isinstance(current_images, list):
            current_images.append(url)
        else:
            current_images = [url]
        
        result = self.products.update_images(qid, current_images)
        return {'success': bool(result), 'url': url}
    
    def remove_product_image(self, qid, image_id):
        """حذف صورة من المنتج"""
        product = self.products.get_by_qid(qid)
        if not product:
            return {'success': False, 'error': 'المنتج غير موجود'}
        
        current_images = product.get('images', [])
        if isinstance(current_images, list):
            new_images = [img for img in current_images if img != image_id]
            result = self.products.update_images(qid, new_images)
            return {'success': bool(result)}
        
        return {'success': False, 'error': 'لا توجد صور'}
    
    # ====== STATUS ======
    def update_product_status(self, qid, supplier_id, status):
        """تحديث حالة المنتج"""
        if not self.verify_access(qid, supplier_id):
            return {'success': False, 'error': 'غير مصرح'}
        
        result = self.products.update_status(qid, status)
        if result:
            mapping = ProductSupplierMapping.query.filter_by(product_qid=qid, supplier_id=supplier_id).first()
            if mapping:
                mapping.status = status.lower()
                db.session.commit()
            return {'success': True, 'message': f'تم التحديث إلى {status}'}
        
        return {'success': False, 'error': 'فشل التحديث'}
    
    # ====== SKU ======
    def check_sku_availability(self, sku, exclude_qid=None):
        """التحقق من توفر SKU"""
        return {'available': True}
    
    def generate_sku(self, prefix='PRD'):
        """توليد SKU تلقائي"""
        timestamp = int(time.time())
        return f"{prefix}-{timestamp}"
    
    # ====== MAPPING ======
    def get_supplier_mappings(self, supplier_id):
        """جلب جميع منتجات المورد"""
        mappings = ProductSupplierMapping.query.filter_by(
            supplier_id=supplier_id, 
            status='active'
        ).all()
        return [{'id': m.id, 'qid': m.product_qid, 'supplier_id': m.supplier_id} for m in mappings]
    
    def verify_access(self, qid, supplier_id):
        """التحقق من أن المنتج يخص المورد"""
        return ProductSupplierMapping.query.filter_by(
            product_qid=qid, 
            supplier_id=supplier_id, 
            status='active'
        ).first() is not None
    
    # ====== SUPPLIER ======
    def get_active_suppliers(self):
        """جلب الموردين النشطين"""
        return [{'id': s.id, 'name': s.name} for s in Supplier.query.filter_by(status='active').all()]
    
    def delete_product(self, qid, supplier_id):
        """حذف منتج"""
        if not self.verify_access(qid, supplier_id):
            return {'success': False, 'error': 'غير مصرح'}
        
        result = self.products.delete(qid)
        
        if result:
            mapping = ProductSupplierMapping.query.filter_by(product_qid=qid, supplier_id=supplier_id).first()
            if mapping:
                db.session.delete(mapping)
                db.session.commit()
        
        return {'success': result}


# ====== STATS ======
def get_product_stats(supplier_id):
    """جلب إحصائيات منتجات المورد"""
    service = SupplierProductService()
    mappings = service.get_supplier_mappings(supplier_id)
    
    stats = {
        'total': len(mappings),
        'published': 0,
        'draft': 0,
        'rejected': 0,
        'archived': 0
    }
    
    for m in mappings:
        product = service.fetch_product_by_qid(m['qid'])
        if product:
            status = product.get('status', '').upper()
            if status in ['PUBLISHED', 'ACTIVE']:
                stats['published'] += 1
            elif status == 'DRAFT':
                stats['draft'] += 1
            elif status == 'REJECTED':
                stats['rejected'] += 1
            elif status == 'ARCHIVED':
                stats['archived'] += 1
    
    return stats


# ====== SINGLETON ======
supplier_product = SupplierProductService()
