# coding: utf-8
# 📂 apps/suppliers_product/services.py

from apps.services.product_sync_service import ProductSyncService as QumraSyncService
from apps.services.product_mapping_service import product_mapping
from apps.services.product_ident_mutation import product_ident
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models import Supplier
from apps.suppliers_product.helpers import compress_image
import logging
import time

logger = logging.getLogger(__name__)


class SupplierProductService:
    def __init__(self):
        self.qumra = QumraSyncService()

    # ====== GET ======
    def get_product(self, qid, supplier_id):
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=qid, supplier_id=supplier_id, status='active'
        ).first()
        if not mapping:
            return {'success': False, 'error': 'المنتج غير موجود'}
        product = self.qumra.fetch_product_by_qid(qid)
        if not product:
            return {'success': False, 'error': 'المنتج غير موجود في قمرة'}
        return {'success': True, 'product': product, 'mapping': product_mapping.get_mapping_by_qid(qid)}

    def fetch_product_by_qid(self, qid):
        return self.qumra.fetch_product_by_qid(qid)

    # ====== CREATE ======
    def create_product(self, supplier_id, data):
        supplier = Supplier.query.get(supplier_id)
        if not supplier:
            return {'success': False, 'error': 'المورد غير موجود'}

        title = data.get('title', '').strip()
        if not title:
            return {'success': False, 'error': 'اسم المنتج مطلوب'}

        product_data = {
            'title': title,
            'description': data.get('description', '').strip(),
            'price': float(data.get('price', 0)),
            'status': data.get('status', 'DRAFT')
        }

        if data.get('sku'):
            sku = data['sku'].strip()
            if not product_ident.check_sku_availability(sku).get('available', True):
                return {'success': False, 'error': f'SKU "{sku}" غير متاح'}
            product_data['sku'] = sku

        if data.get('weight'):
            product_data['weight'] = float(data['weight'])
        if data.get('quantity'):
            product_data['quantity'] = int(data['quantity'])

        if data.get('image_file'):
            url = self._upload_image(data['image_file'], data.get('image_filename', 'image.jpg'))
            if url:
                product_data['images'] = [url]

        # ✅ إضافة supplier_id إلى create_product
        result = self.qumra.create_product(**product_data, supplier_id=supplier_id)
        
        # ✅ إذا نجح الإنشاء، تأكد من ربط المنتج بالمورد
        if result and result.get('success'):
            qid = result.get('qid')
            if qid:
                # ✅ التحقق من وجود الربط
                existing_mapping = ProductSupplierMapping.query.filter_by(product_qid=qid).first()
                if not existing_mapping:
                    mapping = ProductSupplierMapping(
                        product_qid=qid,
                        supplier_id=supplier_id,
                        status='active'
                    )
                    from apps.extensions import db
                    db.session.add(mapping)
                    db.session.commit()
                    logger.info(f"✅ تم ربط المنتج {qid} بالمورد {supplier_id}")
        
        return result

    # ====== UPDATE ======
    def update_product(self, qid, supplier_id, data):
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=qid, supplier_id=supplier_id, status='active'
        ).first()
        if not mapping:
            return {'success': False, 'error': 'المنتج غير موجود'}

        if data.get('title') or data.get('description') or data.get('status'):
            info = {}
            if data.get('title'): info['title'] = data['title']
            if data.get('description'): info['description'] = data['description']
            if data.get('status'): info['status'] = data['status']
            if info:
                self.qumra.update_product_info(qid, **info)

        if data.get('price'):
            self.qumra.update_product_pricing(qid, float(data['price']))
        if data.get('weight'):
            self.qumra.update_product_weight(qid, float(data['weight']))

        if data.get('sku'):
            sku = data['sku'].strip()
            if product_ident.check_sku_availability(sku, qid).get('available', True):
                product_ident.update_product_sku(qid, sku)
            else:
                return {'success': False, 'error': f'SKU "{sku}" غير متاح'}

        if data.get('image_file'):
            result = self.add_product_image(qid, data['image_file'], data.get('image_filename', 'image.jpg'))
            if not result['success']:
                return result

        return {'success': True, 'message': 'تم التحديث'}

    # ====== IMAGE ======
    def _upload_image(self, image_data, filename):
        return self.qumra.upload_image(compress_image(image_data), filename)

    def add_product_image(self, qid, image_data, filename):
        url = self._upload_image(image_data, filename)
        if not url:
            return {'success': False, 'error': 'فشل رفع الصورة'}
        product = self.qumra.fetch_product_by_qid(qid)
        urls = [img.get('fileUrl') for img in product.get('images', []) if img.get('fileUrl')]
        urls.append(url)
        return {'success': self.qumra.update_product_images(qid, urls), 'url': url}

    def remove_product_image(self, qid, image_id):
        product = self.qumra.fetch_product_by_qid(qid)
        if not product:
            return {'success': False, 'error': 'المنتج غير موجود'}
        urls = [img.get('fileUrl') for img in product.get('images', []) if img.get('_id') != image_id and img.get('fileUrl')]
        return {'success': self.qumra.update_product_images(qid, urls)}

    # ====== STATUS ======
    def update_product_status(self, qid, supplier_id, status):
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=qid, supplier_id=supplier_id, status='active'
        ).first()
        if not mapping:
            return {'success': False, 'error': 'المنتج غير موجود'}
        if self.qumra.update_product_status(qid, status):
            product_mapping.update_mapping_status(qid, status)
            return {'success': True, 'message': f'تم التحديث إلى {status}'}
        return {'success': False, 'error': 'فشل التحديث'}

    # ====== SKU ======
    def check_sku_availability(self, sku, exclude_qid=None):
        return product_ident.check_sku_availability(sku, exclude_qid)

    def generate_sku(self, prefix='PRD'):
        try:
            return product_ident.generate_sku(prefix=prefix)
        except Exception:
            return f"{prefix}-{int(time.time())}"

    # ====== MAPPING ======
    def get_supplier_mappings(self, supplier_id):
        mappings = ProductSupplierMapping.query.filter_by(supplier_id=supplier_id, status='active').all()
        return [{'id': m.id, 'qid': m.product_qid, 'supplier_id': m.supplier_id} for m in mappings]

    def verify_access(self, qid, supplier_id):
        return ProductSupplierMapping.query.filter_by(
            product_qid=qid, supplier_id=supplier_id, status='active'
        ).first() is not None

    # ====== SUPPLIER ======
    def get_active_suppliers(self):
        return [{'id': s.id, 'name': s.name} for s in Supplier.query.filter_by(status='active').all()]

    def delete_product(self, qid, supplier_id):
        if not self.verify_access(qid, supplier_id):
            return {'success': False, 'error': 'غير مصرح'}
        return {'success': self.qumra.delete_product(qid, delete_mapping=True)}


# ====== STATS ======
def get_product_stats(supplier_id):
    service = SupplierProductService()
    mappings = service.get_supplier_mappings(supplier_id)
    stats = {'total': len(mappings), 'published': 0, 'draft': 0, 'rejected': 0, 'archived': 0}
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


supplier_product = SupplierProductService()
