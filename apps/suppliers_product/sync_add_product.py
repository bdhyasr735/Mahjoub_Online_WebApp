# coding: utf-8
# 📂 apps/suppliers_product/sync_add_product.py

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
    """ضغط الصورة وتقليل حجمها"""
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


class AddProductSyncService:
    """خدمة إنشاء وإضافة المنتجات"""

    def __init__(self):
        self.sync_service = ProductSyncService()

    # ============================================================
    # 📝 CREATE PRODUCT - إنشاء منتج
    # ============================================================

    def create_product(self, supplier_id: int, data: dict) -> dict:
        """
        إنشاء منتج جديد وربطه بالمورد
        
        Args:
            supplier_id: معرف المورد
            data: بيانات المنتج {
                'title': str,
                'description': str,
                'price': float,
                'status': str,
                'sku': str,
                'weight': float,
                'quantity': int,
                'image_file': bytes (اختياري),
                'image_filename': str (اختياري)
            }
        
        Returns:
            dict: {'success': bool, 'qid': str, 'message': str, 'error': str}
        """
        try:
            # 1️⃣ التحقق من وجود المورد
            supplier = Supplier.query.get(supplier_id)
            if not supplier:
                return {
                    'success': False,
                    'error': 'المورد غير موجود'
                }

            # 2️⃣ التحقق من البيانات المطلوبة
            title = data.get('title', '').strip()
            if not title:
                return {
                    'success': False,
                    'error': 'اسم المنتج مطلوب'
                }

            # 3️⃣ تجهيز بيانات المنتج
            product_data = {
                'title': title,
                'description': data.get('description', '').strip(),
                'price': float(data.get('price', 0)),
                'status': data.get('status', 'DRAFT')
            }

            # إضافة الحقول الاختيارية
            if data.get('sku'):
                sku = data['sku'].strip()
                # التحقق من توفر SKU
                availability = product_ident.check_sku_availability(sku)
                if not availability.get('available', True):
                    return {
                        'success': False,
                        'error': f'SKU "{sku}" غير متاح'
                    }
                product_data['sku'] = sku

            if data.get('weight'):
                product_data['weight'] = float(data['weight'])

            if data.get('quantity'):
                product_data['quantity'] = int(data['quantity'])

            # 4️⃣ معالجة الصورة (إن وجدت)
            if data.get('image_file'):
                image_result = self._upload_and_get_url(
                    data['image_file'],
                    data.get('image_filename', 'image.jpg')
                )
                if image_result['success']:
                    product_data['images'] = [image_result['url']]
                else:
                    # لا نمنع إنشاء المنتج بسبب فشل الصورة
                    logger.warning(f"⚠️ فشل رفع الصورة: {image_result['error']}")

            # 5️⃣ إنشاء المنتج في قمرة مع الربط
            result = self.sync_service.create_product(
                **product_data,
                supplier_id=supplier_id
            )

            if result.get('success'):
                return {
                    'success': True,
                    'qid': result.get('qid'),
                    'message': 'تم إنشاء المنتج بنجاح',
                    'data': result.get('data')
                }
            else:
                return {
                    'success': False,
                    'error': result.get('message', 'فشل إنشاء المنتج')
                }

        except Exception as e:
            logger.error(f"❌ خطأ في create_product: {e}")
            traceback.print_exc()
            return {
                'success': False,
                'error': f'خطأ: {str(e)}'
            }

    # ============================================================
    # 🖼️ IMAGE OPERATIONS - عمليات الصور
    # ============================================================

    def _upload_and_get_url(self, image_data: bytes, filename: str) -> dict:
        """رفع صورة وإرجاع رابطها"""
        try:
            # ضغط الصورة
            compressed_data = compress_image(image_data)

            # رفع الصورة
            image_url = self.sync_service.upload_image(compressed_data, filename)

            if image_url:
                return {
                    'success': True,
                    'url': image_url
                }

            return {
                'success': False,
                'error': 'فشل رفع الصورة'
            }

        except Exception as e:
            logger.error(f"❌ خطأ في _upload_and_get_url: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def upload_product_image(self, qid: str, supplier_id: int, image_data: bytes, filename: str) -> dict:
        """رفع صورة لمنتج موجود"""
        try:
            # التحقق من الصلاحية
            if not self.verify_access(qid, supplier_id):
                return {
                    'success': False,
                    'error': 'غير مصرح بهذا المنتج'
                }

            # رفع الصورة
            image_result = self._upload_and_get_url(image_data, filename)

            if not image_result['success']:
                return image_result

            # إضافة الصورة للمنتج
            product = self.sync_service.fetch_product_by_qid(qid)
            current_images = product.get('images', []) if product else []
            current_urls = [img.get('fileUrl') for img in current_images if img.get('fileUrl')]
            current_urls.append(image_result['url'])

            success = self.sync_service.update_product_images(qid, current_urls)

            if success:
                return {
                    'success': True,
                    'message': 'تم إضافة الصورة بنجاح',
                    'url': image_result['url']
                }

            return {
                'success': False,
                'error': 'فشل تحديث صور المنتج'
            }

        except Exception as e:
            logger.error(f"❌ خطأ في upload_product_image: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    # ============================================================
    # 🔍 SKU OPERATIONS - عمليات SKU
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
    # 📊 GET SUPPLIER - جلب بيانات المورد
    # ============================================================

    def get_supplier(self, supplier_id: int) -> dict:
        """جلب بيانات المورد"""
        try:
            supplier = Supplier.query.get(supplier_id)
            if not supplier:
                return {'success': False, 'error': 'المورد غير موجود'}

            return {
                'success': True,
                'data': {
                    'id': supplier.id,
                    'name': supplier.name,
                    'status': supplier.status
                }
            }
        except Exception as e:
            logger.error(f"❌ خطأ في get_supplier: {e}")
            return {'success': False, 'error': str(e)}

    # ============================================================
    # 📋 GET SUPPLIERS - جلب جميع الموردين
    # ============================================================

    def get_active_suppliers(self) -> list:
        """جلب قائمة الموردين النشطين"""
        try:
            suppliers = Supplier.query.filter_by(status='active').all()
            return [{
                'id': s.id,
                'name': s.name
            } for s in suppliers]
        except Exception as e:
            logger.error(f"❌ خطأ في get_active_suppliers: {e}")
            return []


# ============================================================
# 🚀 SINGLETON INSTANCE
# ============================================================

add_sync = AddProductSyncService()
