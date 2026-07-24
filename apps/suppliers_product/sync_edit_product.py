# coding: utf-8
# 📂 apps/suppliers_product/sync_edit_product.py

from apps.services.product_sync_service import ProductSyncService
from apps.services.product_mapping_service import product_mapping
from apps.services.product_ident_mutation import product_ident
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier import Supplier
from apps.extensions import db
import base64
import traceback
import logging
from io import BytesIO
from PIL import Image

logger = logging.getLogger(__name__)


def compress_image(image_data, max_size=(600, 600), quality=40):
    """ضغط الصورة"""
    try:
        img = Image.open(BytesIO(image_data))
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
    except Exception as e:
        logger.warning(f"⚠️ خطأ في ضغط الصورة: {e}")
        return image_data


class EditProductSyncService:
    """خدمة مزامنة وتحديث المنتجات"""

    def __init__(self):
        self.sync_service = ProductSyncService()

    # ============================================================
    # 🔍 GET PRODUCT - جلب المنتج
    # ============================================================

    def get_product(self, qid: str, supplier_id: int) -> dict:
        """جلب بيانات المنتج مع التحقق من الصلاحية"""
        # التحقق من الربط
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=qid,
            supplier_id=supplier_id,
            status='active'
        ).first()

        if not mapping:
            return {'success': False, 'error': 'المنتج غير موجود أو غير مصرح'}

        # جلب بيانات المنتج من قمرة
        product = self.sync_service.fetch_product_by_qid(qid)

        if not product:
            return {'success': False, 'error': 'المنتج غير موجود في قمرة'}

        # جلب بيانات الربط
        mapping_data = product_mapping.get_mapping_by_qid(qid)

        return {
            'success': True,
            'product': product,
            'mapping': mapping_data,
            'supplier': Supplier.query.get(supplier_id)
        }

    # ============================================================
    # ✏️ UPDATE PRODUCT - تحديث المنتج
    # ============================================================

    def update_product(self, qid: str, supplier_id: int, data: dict) -> dict:
        """تحديث بيانات المنتج"""
        try:
            # التحقق من الصلاحية
            mapping = ProductSupplierMapping.query.filter_by(
                product_qid=qid,
                supplier_id=supplier_id,
                status='active'
            ).first()

            if not mapping:
                return {'success': False, 'error': 'المنتج غير موجود أو غير مصرح'}

            # تحديث المعلومات الأساسية
            if data.get('title') or data.get('description') or data.get('status'):
                update_info = {}
                if data.get('title'):
                    update_info['title'] = data['title']
                if data.get('description'):
                    update_info['description'] = data['description']
                if data.get('status'):
                    update_info['status'] = data['status']
                if update_info:
                    self.sync_service.update_product_info(qid, **update_info)

            # تحديث السعر
            if data.get('price'):
                self.sync_service.update_product_pricing(qid, float(data['price']))

            # تحديث الوزن
            if data.get('weight'):
                self.sync_service.update_product_weight(qid, float(data['weight']))

            # تحديث الكمية
            if data.get('quantity'):
                # ملاحظة: قد تحتاج إلى mutation منفصل للكمية
                pass

            # تحديث SKU
            if data.get('sku'):
                sku = data['sku'].strip()
                availability = product_ident.check_sku_availability(sku, qid)
                if availability.get('available', True):
                    product_ident.update_product_sku(qid, sku)
                else:
                    return {
                        'success': False,
                        'error': f'SKU "{sku}" غير متاح'
                    }

            # تحديث الصورة (إن وجدت)
            if data.get('image_file'):
                image_result = self.add_product_image(
                    qid, 
                    data['image_file'],
                    data.get('image_filename', 'image.jpg')
                )
                if not image_result['success']:
                    return image_result

            # تحديث حالة الربط
            if data.get('mapping_status'):
                product_mapping.update_mapping_status(qid, data['mapping_status'])

            return {
                'success': True,
                'message': 'تم تحديث المنتج بنجاح'
            }

        except Exception as e:
            logger.error(f"❌ خطأ في update_product: {e}")
            traceback.print_exc()
            return {
                'success': False,
                'error': f'خطأ: {str(e)}'
            }

    # ============================================================
    # 🖼️ IMAGE OPERATIONS - عمليات الصور
    # ============================================================

    def add_product_image(self, qid: str, image_data: bytes, filename: str) -> dict:
        """إضافة صورة للمنتج"""
        try:
            # ضغط الصورة
            compressed_data = compress_image(image_data)

            # رفع الصورة
            image_url = self.sync_service.upload_image(compressed_data, filename)

            if not image_url:
                return {'success': False, 'error': 'فشل رفع الصورة'}

            # جلب الصور الحالية
            product = self.sync_service.fetch_product_by_qid(qid)
            current_images = product.get('images', []) if product else []
            current_urls = [img.get('fileUrl') for img in current_images if img.get('fileUrl')]
            current_urls.append(image_url)

            # تحديث صور المنتج
            success = self.sync_service.update_product_images(qid, current_urls)

            if success:
                return {
                    'success': True,
                    'message': 'تم إضافة الصورة بنجاح',
                    'url': image_url
                }

            return {'success': False, 'error': 'فشل تحديث صور المنتج'}

        except Exception as e:
            logger.error(f"❌ خطأ في add_product_image: {e}")
            return {'success': False, 'error': str(e)}

    def remove_product_image(self, qid: str, image_id: str) -> dict:
        """حذف صورة من المنتج"""
        try:
            # جلب المنتج
            product = self.sync_service.fetch_product_by_qid(qid)
            if not product:
                return {'success': False, 'error': 'المنتج غير موجود'}

            # تصفية الصور
            current_images = product.get('images', [])
            filtered_images = [img for img in current_images if img.get('_id') != image_id]
            current_urls = [img.get('fileUrl') for img in filtered_images if img.get('fileUrl')]

            # تحديث الصور
            success = self.sync_service.update_product_images(qid, current_urls)

            if success:
                return {'success': True, 'message': 'تم حذف الصورة بنجاح'}

            return {'success': False, 'error': 'فشل حذف الصورة'}

        except Exception as e:
            logger.error(f"❌ خطأ في remove_product_image: {e}")
            return {'success': False, 'error': str(e)}

    # ============================================================
    # 📊 STATUS OPERATIONS - عمليات الحالة
    # ============================================================

    def update_product_status(self, qid: str, supplier_id: int, status: str) -> dict:
        """تحديث حالة المنتج"""
        try:
            # التحقق من الصلاحية
            mapping = ProductSupplierMapping.query.filter_by(
                product_qid=qid,
                supplier_id=supplier_id,
                status='active'
            ).first()

            if not mapping:
                return {'success': False, 'error': 'المنتج غير موجود أو غير مصرح'}

            # تحديث الحالة في قمرة
            success = self.sync_service.update_product_status(qid, status)

            if success:
                # تحديث حالة الربط
                product_mapping.update_mapping_status(qid, status)
                return {'success': True, 'message': f'تم تحديث الحالة إلى {status}'}

            return {'success': False, 'error': 'فشل تحديث حالة المنتج'}

        except Exception as e:
            logger.error(f"❌ خطأ في update_product_status: {e}")
            return {'success': False, 'error': str(e)}

    # ============================================================
    # 🔢 SKU OPERATIONS - عمليات SKU
    # ============================================================

    def check_sku_availability(self, sku: str, exclude_qid: str = None) -> dict:
        """التحقق من توفر SKU"""
        try:
            return product_ident.check_sku_availability(sku, exclude_qid)
        except Exception as e:
            logger.error(f"❌ خطأ في check_sku_availability: {e}")
            return {'available': False, 'message': str(e)}

    def generate_sku(self, prefix: str = 'PRD') -> str:
        """توليد SKU تلقائي"""
        try:
            return product_ident.generate_sku(prefix=prefix)
        except Exception as e:
            logger.error(f"❌ خطأ في generate_sku: {e}")
            # توليد SKU بديل
            import time
            return f"{prefix}-{int(time.time())}"

    # ============================================================
    # 🔍 HELPER - التحقق من الصلاحية
    # ============================================================

    def verify_access(self, qid: str, supplier_id: int) -> bool:
        """التحقق من صلاحية المورد على المنتج"""
        mapping = ProductSupplierMapping.query.filter_by(
            product_qid=qid,
            supplier_id=supplier_id,
            status='active'
        ).first()
        return mapping is not None


# ============================================================
# 🚀 SINGLETON INSTANCE
# ============================================================

edit_sync = EditProductSyncService()
