# coding: utf-8
# apps/suppliers_product/add_product_services.py

import logging
import uuid
from flask import current_app

logger = logging.getLogger(__name__)

class AddProductService:
    """خدمة إدارة وإضافة المنتجات لمنصة محجوب أونلاين"""

    @staticmethod
    def create_product(product_data, image_url=None):
        """
        معالجة منطق إنشاء وإضافة منتج جديد وتجهيزه للتخزين
        
        :param product_data: قاموس يحتوي على بيانات المنتج (العنوان، السعر، الكمية، إلخ)
        :param image_url: رابط الصورة المرفوعة إن وجدت
        :return: قاموس يمثل المنتج المضاف أو يرفع استثناء عند الفشل
        """
        try:
            # توليد معرف فريد QID و SKU إذا لم يتوفران
            prod_qid = product_data.get('qid') or f"PROD_{uuid.uuid4().hex[:8].upper()}"
            sku = product_data.get('sku') or f"SKU_{uuid.uuid4().hex[:6].upper()}"

            # تنسيق القيم العددية بعناية فائقة
            price = float(product_data.get('price', 0.0))
            quantity = int(product_data.get('quantity', 0))
            weight = float(product_data.get('weight', 0.0))

            # تجهيز هيكل بيانات المنتج النهائي
            processed_product = {
                "qid": prod_qid,
                "name": product_data.get('title') or product_data.get('name', ''),
                "description": product_data.get('description', ''),
                "price": price,
                "quantity": quantity,
                "sku": sku,
                "weight": weight,
                "status": product_data.get('status', 'DRAFT'),
                "images": [{"url": image_url}] if image_url else []
            }

            # تسجيل العمليات في السجلات الرسمية
            logger.info(f"تم إنشاء المنتج بنجاح في طبقة الخدمة برقم: {prod_qid}")
            
            return {
                "success": True,
                "message": "تمت معالجة وتخزين المنتج بنجاح",
                "product": processed_product
            }

        except ValueError as ve:
            logger.error(f"خطأ في تحويل بيانات المنتج: {str(ve)}")
            raise ValueError(f"بيانات مدخلة غير صالحة: {str(ve)}")
        except Exception as e:
            logger.error(f"خطأ غير متوقع في خدمة إضافة المنتج: {str(e)}")
            raise RuntimeError(f"فشل معالجة المنتج: {str(e)}")

    @staticmethod
    def validate_product_data(product_data):
        """
        التحقق من صحة حقول المنتج قبل اعتمادها في النظام
        
        :param product_data: بيانات المنتج الواردة من الطلب
        :return: قائمة الأخطاء إن وجدت، أو قائمة فارغة إذا كانت البيانات سليمة
        """
        errors = []
        
        title = product_data.get('title') or product_data.get('name', '')
        if not title.strip():
            errors.append("اسم المنتج مطلوب ولا يمكن أن يكون فارغاً.")

        price = product_data.get('price')
        if price is None or str(price).strip() == '':
            errors.append("سعر المنتج مطلوب.")
        else:
            try:
                parsed_price = float(price)
                if parsed_price < 0:
                    errors.append("سعر المنتج لا يمكن أن يكون سالباً.")
            except ValueError:
                errors.append("سعر المنتج يجب أن يكون رقماً صالحاً.")

        quantity = product_data.get('quantity')
        if quantity is not None and str(quantity).strip() != '':
            try:
                if int(quantity) < 0:
                    errors.append("الكمية لا يمكن أن تكون سالبة.")
            except ValueError:
                errors.append("الكمية يجب أن تكون عدداً صحيحاً.")

        return errors
