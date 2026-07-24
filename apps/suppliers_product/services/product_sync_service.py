# coding: utf-8
# 📂 apps/suppliers_product/services/product_sync_service.py

"""
الخدمة الأساسية لإدارة منتجات الموردين
تستخدم كطبقة وسيطة بين الـ Services العامة ومنطق الموردين
"""

from apps.services.product_sync_service import ProductSyncService as QumraSyncService
from apps.services.product_mapping_service import product_mapping
from apps.services.product_ident_mutation import product_ident
from apps.models.product_supplier_map import ProductSupplierMapping
from apps.models.supplier import Supplier
from apps.extensions import db
import logging
from io import BytesIO
from PIL import Image
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


# ============================================================
# 🔧 HELPER FUNCTIONS - دوال مساعدة
# ============================================================

def compress_image(image_data: bytes, max_size: tuple = (600, 600), quality: int = 40) -> bytes:
    """
    ضغط الصورة وتقليل حجمها
    
    Args:
        image_data: بيانات الصورة (bytes)
        max_size: الأبعاد القصوى (width, height)
        quality: جودة الضغط (1-100)
    
    Returns:
        bytes: بيانات الصورة المضغوطة
    """
    try:
        img = Image.open(BytesIO(image_data))
        
        # تحويل إلى RGB إذا كانت RGBA
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # تصغير الأبعاد إذا كانت أكبر من الحد الأقصى
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # حفظ الصورة المضغوطة
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        return output.getvalue()
        
    except Exception as e:
        logger.warning(f"⚠️ خطأ في ضغط الصورة: {e}")
        return image_data


# ============================================================
# 🚀 MAIN SERVICE - الخدمة الرئيسية
# ============================================================

class SupplierProductService:
    """
    خدمة موحدة لإدارة منتجات الموردين
    تحتوي على: إنشاء، تعديل، حذف، جلب، صور، SKU
    """
    
    def __init__(self):
        """تهيئة الخدمة"""
        self.qumra = QumraSyncService()
    
    # ============================================================
    # 🔍 GET PRODUCT - جلب المنتج
    # ============================================================
    
    def get_product(self, qid: str, supplier_id: int) -> dict:
        """
        جلب بيانات المنتج مع التحقق من الصلاحية
        
        Args:
            qid: معرف المنتج في قمرة
            supplier_id: معرف المورد
        
        Returns:
            dict: {
                'success': bool,
                'product': dict,
                'mapping': dict,
                'supplier': dict,
                'error': str
            }
        """
        try:
            # 1️⃣ التحقق من الربط في قاعدة البيانات
            mapping = ProductSupplierMapping.query.filter_by(
                product_qid=qid,
                supplier_id=supplier_id,
                status='active'
            ).first()
            
            if not mapping:
                return {
                    'success': False,
                    'error': 'المنتج غير موجود أو غير مصرح'
                }
            
            # 2️⃣ جلب بيانات المنتج من قمرة
            product = self.qumra.fetch_product_by_qid(qid)
            
            if not product:
                return {
                    'success': False,
                    'error': 'المنتج غير موجود في قمرة'
                }
            
            # 3️⃣ جلب بيانات الربط من service
            mapping_data = product_mapping.get_mapping_by_qid(qid)
            
            # 4️⃣ جلب بيانات المورد
            supplier = Supplier.query.get(supplier_id)
            
            return {
                'success': True,
                'product': product,
                'mapping': mapping_data,
                'supplier': {
                    'id': supplier.id,
                    'name': supplier.name
                } if supplier else None
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في get_product: {e}")
            return {
                'success': False,
                'error': f'خطأ: {str(e)}'
            }
    
    def fetch_product_by_qid(self, qid: str) -> Optional[Dict]:
        """
        جلب بيانات المنتج من قمرة مباشرة (بدون التحقق من الصلاحية)
        
        Args:
            qid: معرف المنتج في قمرة
        
        Returns:
            Dict: بيانات المنتج أو None
        """
        return self.qumra.fetch_product_by_qid(qid)
    
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
            
            # إضافة SKU مع التحقق من التوفر
            if data.get('sku'):
                sku = data['sku'].strip()
                availability = product_ident.check_sku_availability(sku)
                if not availability.get('available', True):
                    return {
                        'success': False,
                        'error': f'SKU "{sku}" غير متاح'
                    }
                product_data['sku'] = sku
            
            # إضافة الوزن
            if data.get('weight'):
                product_data['weight'] = float(data['weight'])
            
            # إضافة الكمية
            if data.get('quantity'):
                product_data['quantity'] = int(data['quantity'])
            
            # 4️⃣ معالجة الصورة (إن وجدت)
            if data.get('image_file'):
                image_result = self._upload_image(
                    data['image_file'],
                    data.get('image_filename', 'image.jpg')
                )
                if image_result['success']:
                    product_data['images'] = [image_result['url']]
                else:
                    logger.warning(f"⚠️ فشل رفع الصورة: {image_result['error']}")
            
            # 5️⃣ إنشاء المنتج في قمرة مع الربط
            result = self.qumra.create_product(
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
            return {
                'success': False,
                'error': f'خطأ: {str(e)}'
            }
    
    # ============================================================
    # ✏️ UPDATE PRODUCT - تحديث المنتج
    # ============================================================
    
    def update_product(self, qid: str, supplier_id: int, data: dict) -> dict:
        """
        تحديث بيانات المنتج
        
        Args:
            qid: معرف المنتج في قمرة
            supplier_id: معرف المورد
            data: بيانات التحديث {
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
            dict: {'success': bool, 'message': str, 'error': str}
        """
        try:
            # 1️⃣ التحقق من الصلاحية
            mapping = ProductSupplierMapping.query.filter_by(
                product_qid=qid,
                supplier_id=supplier_id,
                status='active'
            ).first()
            
            if not mapping:
                return {
                    'success': False,
                    'error': 'المنتج غير موجود أو غير مصرح'
                }
            
            # 2️⃣ تحديث المعلومات الأساسية
            if data.get('title') or data.get('description') or data.get('status'):
                update_info = {}
                if data.get('title'):
                    update_info['title'] = data['title']
                if data.get('description'):
                    update_info['description'] = data['description']
                if data.get('status'):
                    update_info['status'] = data['status']
                if update_info:
                    self.qumra.update_product_info(qid, **update_info)
            
            # 3️⃣ تحديث السعر
            if data.get('price'):
                self.qumra.update_product_pricing(qid, float(data['price']))
            
            # 4️⃣ تحديث الوزن
            if data.get('weight'):
                self.qumra.update_product_weight(qid, float(data['weight']))
            
            # 5️⃣ تحديث SKU (مع التحقق من التوفر)
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
            
            # 6️⃣ تحديث الصورة (إن وجدت)
            if data.get('image_file'):
                image_result = self.add_product_image(
                    qid,
                    data['image_file'],
                    data.get('image_filename', 'image.jpg')
                )
                if not image_result['success']:
                    return image_result
            
            return {
                'success': True,
                'message': 'تم تحديث المنتج بنجاح'
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في update_product: {e}")
            return {
                'success': False,
                'error': f'خطأ: {str(e)}'
            }
    
    # ============================================================
    # 🖼️ IMAGE OPERATIONS - عمليات الصور
    # ============================================================
    
    def _upload_image(self, image_data: bytes, filename: str) -> dict:
        """
        رفع صورة وإرجاع رابطها (داخلي)
        
        Args:
            image_data: بيانات الصورة
            filename: اسم الملف
        
        Returns:
            dict: {'success': bool, 'url': str, 'error': str}
        """
        try:
            # ضغط الصورة
            compressed_data = compress_image(image_data)
            
            # رفع الصورة
            image_url = self.qumra.upload_image(compressed_data, filename)
            
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
            logger.error(f"❌ خطأ في _upload_image: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def add_product_image(self, qid: str, image_data: bytes, filename: str) -> dict:
        """
        إضافة صورة للمنتج
        
        Args:
            qid: معرف المنتج
            image_data: بيانات الصورة
            filename: اسم الملف
        
        Returns:
            dict: {'success': bool, 'message': str, 'url': str, 'error': str}
        """
        try:
            # 1️⃣ رفع الصورة
            upload_result = self._upload_image(image_data, filename)
            
            if not upload_result['success']:
                return upload_result
            
            # 2️⃣ جلب الصور الحالية
            product = self.qumra.fetch_product_by_qid(qid)
            current_images = product.get('images', []) if product else []
            current_urls = [img.get('fileUrl') for img in current_images if img.get('fileUrl')]
            current_urls.append(upload_result['url'])
            
            # 3️⃣ تحديث صور المنتج
            success = self.qumra.update_product_images(qid, current_urls)
            
            if success:
                return {
                    'success': True,
                    'message': 'تم إضافة الصورة بنجاح',
                    'url': upload_result['url']
                }
            
            return {
                'success': False,
                'error': 'فشل تحديث صور المنتج'
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في add_product_image: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def remove_product_image(self, qid: str, image_id: str) -> dict:
        """
        حذف صورة من المنتج
        
        Args:
            qid: معرف المنتج
            image_id: معرف الصورة
        
        Returns:
            dict: {'success': bool, 'message': str, 'error': str}
        """
        try:
            # 1️⃣ جلب المنتج
            product = self.qumra.fetch_product_by_qid(qid)
            if not product:
                return {
                    'success': False,
                    'error': 'المنتج غير موجود'
                }
            
            # 2️⃣ تصفية الصور
            current_images = product.get('images', [])
            filtered_images = [img for img in current_images if img.get('_id') != image_id]
            current_urls = [img.get('fileUrl') for img in filtered_images if img.get('fileUrl')]
            
            # 3️⃣ تحديث الصور
            success = self.qumra.update_product_images(qid, current_urls)
            
            if success:
                return {
                    'success': True,
                    'message': 'تم حذف الصورة بنجاح'
                }
            
            return {
                'success': False,
                'error': 'فشل حذف الصورة'
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في remove_product_image: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ============================================================
    # 📊 STATUS OPERATIONS - عمليات الحالة
    # ============================================================
    
    def update_product_status(self, qid: str, supplier_id: int, status: str) -> dict:
        """
        تحديث حالة المنتج
        
        Args:
            qid: معرف المنتج
            supplier_id: معرف المورد
            status: الحالة الجديدة (ACTIVE, DRAFT, INACTIVE, ARCHIVED)
        
        Returns:
            dict: {'success': bool, 'message': str, 'error': str}
        """
        try:
            # 1️⃣ التحقق من الصلاحية
            mapping = ProductSupplierMapping.query.filter_by(
                product_qid=qid,
                supplier_id=supplier_id,
                status='active'
            ).first()
            
            if not mapping:
                return {
                    'success': False,
                    'error': 'المنتج غير موجود أو غير مصرح'
                }
            
            # 2️⃣ تحديث الحالة في قمرة
            success = self.qumra.update_product_status(qid, status)
            
            if success:
                # 3️⃣ تحديث حالة الربط
                product_mapping.update_mapping_status(qid, status)
                return {
                    'success': True,
                    'message': f'تم تحديث الحالة إلى {status}'
                }
            
            return {
                'success': False,
                'error': 'فشل تحديث حالة المنتج'
            }
            
        except Exception as e:
            logger.error(f"❌ خطأ في update_product_status: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # ============================================================
    # 🔢 SKU OPERATIONS - عمليات SKU
    # ============================================================
    
    def check_sku_availability(self, sku: str, exclude_qid: str = None) -> dict:
        """
        التحقق من توفر SKU
        
        Args:
            sku: رقم SKU للتحقق
            exclude_qid: معرف المنتج المستثنى (للتحديث)
        
        Returns:
            dict: {'available': bool, 'message': str, 'existing_product': dict}
        """
        try:
            return product_ident.check_sku_availability(sku, exclude_qid)
        except Exception as e:
            logger.error(f"❌ خطأ في check_sku_availability: {e}")
            return {'available': False, 'message': str(e)}
    
    def generate_sku(self, prefix: str = 'PRD') -> str:
        """
        توليد SKU تلقائي
        
        Args:
            prefix: بادئة SKU
        
        Returns:
            str: SKU جديد
        """
        try:
            return product_ident.generate_sku(prefix=prefix)
        except Exception as e:
            logger.error(f"❌ خطأ في generate_sku: {e}")
            # توليد SKU بديل في حالة الفشل
            import time
            return f"{prefix}-{int(time.time())}"
    
    # ============================================================
    # 🔍 HELPER - التحقق من الصلاحية
    # ============================================================
    
    def verify_access(self, qid: str, supplier_id: int) -> bool:
        """
        التحقق من صلاحية المورد على المنتج
        
        Args:
            qid: معرف المنتج
            supplier_id: معرف المورد
        
        Returns:
            bool: True إذا كان المورد يملك المنتج
        """
        try:
            mapping = ProductSupplierMapping.query.filter_by(
                product_qid=qid,
                supplier_id=supplier_id,
                status='active'
            ).first()
            return mapping is not None
        except Exception as e:
            logger.error(f"❌ خطأ في verify_access: {e}")
            return False
    
    # ============================================================
    # 📋 SUPPLIER OPERATIONS - عمليات الموردين
    # ============================================================
    
    def get_active_suppliers(self) -> list:
        """
        جلب قائمة الموردين النشطين
        
        Returns:
            list: [{'id': int, 'name': str}, ...]
        """
        try:
            suppliers = Supplier.query.filter_by(status='active').all()
            return [
                {'id': s.id, 'name': s.name}
                for s in suppliers
            ]
        except Exception as e:
            logger.error(f"❌ خطأ في get_active_suppliers: {e}")
            return []
    
    def get_supplier(self, supplier_id: int) -> dict:
        """
        جلب بيانات المورد
        
        Args:
            supplier_id: معرف المورد
        
        Returns:
            dict: {'success': bool, 'data': dict, 'error': str}
        """
        try:
            supplier = Supplier.query.get(supplier_id)
            if not supplier:
                return {
                    'success': False,
                    'error': 'المورد غير موجود'
                }
            
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
            return {
                'success': False,
                'error': str(e)
            }
    
    # ============================================================
    # 📦 MAPPING OPERATIONS - عمليات الربط
    # ============================================================
    
    def get_supplier_mappings(self, supplier_id: int) -> list:
        """
        جلب جميع علاقات الربط لمورد معين
        
        Args:
            supplier_id: معرف المورد
        
        Returns:
            list: قائمة العلاقات
        """
        try:
            mappings = ProductSupplierMapping.query.filter_by(
                supplier_id=supplier_id,
                status='active'
            ).all()
            
            return [
                {
                    'id': m.id,
                    'qid': m.product_qid,
                    'supplier_id': m.supplier_id,
                    'status': m.status,
                    'created_at': m.created_at.isoformat() if m.created_at else None,
                    'updated_at': m.updated_at.isoformat() if m.updated_at else None
                }
                for m in mappings
            ]
        except Exception as e:
            logger.error(f"❌ خطأ في get_supplier_mappings: {e}")
            return []


# ============================================================
# 🚀 SINGLETON INSTANCE
# ============================================================

supplier_product = SupplierProductService()
