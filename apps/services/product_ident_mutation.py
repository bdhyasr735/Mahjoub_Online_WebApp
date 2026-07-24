# coding: utf-8
# 📂 apps/services/product_ident_mutation.py

from typing import Dict, List, Optional, Any
from .graphql_client import QomrahGraphQLClient


# ============================================================
# 📋 MUTATIONS - تحويرات تعريف المنتج
# ============================================================

# 1️⃣ تحديث تعريف المنتج (الكامل)
UPDATE_PRODUCT_IDENTIFICATION_MUTATION = """
mutation UpdateProductIdentification($qid: String!, $identification: IdentificationInput!) {
    updateProductIdentification(qid: $qid, identification: $identification) {
        id
        qid
        identification {
            sku
            barcode
            barcodeType
            hsCode
            countryOfOrigin
            mpn
        }
        updatedAt
    }
}
"""

# 2️⃣ تحديث SKU فقط
UPDATE_PRODUCT_SKU_MUTATION = """
mutation UpdateProductSKU($qid: String!, $sku: String!) {
    updateProductSKU(qid: $qid, sku: $sku) {
        id
        qid
        identification {
            sku
        }
        updatedAt
    }
}
"""

# 3️⃣ تحديث Barcode فقط
UPDATE_PRODUCT_BARCODE_MUTATION = """
mutation UpdateProductBarcode($qid: String!, $barcode: String!, $barcodeType: String) {
    updateProductBarcode(qid: $qid, barcode: $barcode, barcodeType: $barcodeType) {
        id
        qid
        identification {
            barcode
            barcodeType
        }
        updatedAt
    }
}
"""

# 4️⃣ تحديث HS Code فقط
UPDATE_PRODUCT_HS_CODE_MUTATION = """
mutation UpdateProductHSCode($qid: String!, $hsCode: String!) {
    updateProductHSCode(qid: $qid, hsCode: $hsCode) {
        id
        qid
        identification {
            hsCode
        }
        updatedAt
    }
}
"""

# 5️⃣ تحديث بلد المنشأ
UPDATE_PRODUCT_COUNTRY_OF_ORIGIN_MUTATION = """
mutation UpdateProductCountryOfOrigin($qid: String!, $countryOfOrigin: String!) {
    updateProductCountryOfOrigin(qid: $qid, countryOfOrigin: $countryOfOrigin) {
        id
        qid
        identification {
            countryOfOrigin
        }
        updatedAt
    }
}
"""

# 6️⃣ تحديث MPN (Manufacturer Part Number)
UPDATE_PRODUCT_MPN_MUTATION = """
mutation UpdateProductMPN($qid: String!, $mpn: String!) {
    updateProductMPN(qid: $qid, mpn: $mpn) {
        id
        qid
        identification {
            mpn
        }
        updatedAt
    }
}
"""

# 7️⃣ تحديث تعريف الفاريانت
UPDATE_VARIANT_IDENTIFICATION_MUTATION = """
mutation UpdateVariantIdentification($variantQid: String!, $identification: IdentificationInput!) {
    updateVariantIdentification(variantQid: $variantQid, identification: $identification) {
        id
        qid
        identification {
            sku
            barcode
            barcodeType
            hsCode
            countryOfOrigin
            mpn
        }
        updatedAt
    }
}
"""

# 8️⃣ تحديث SKU للفاريانت
UPDATE_VARIANT_SKU_MUTATION = """
mutation UpdateVariantSKU($variantQid: String!, $sku: String!) {
    updateVariantSKU(variantQid: $variantQid, sku: $sku) {
        id
        qid
        identification {
            sku
        }
        updatedAt
    }
}
"""

# 9️⃣ تحديث Barcode للفاريانت
UPDATE_VARIANT_BARCODE_MUTATION = """
mutation UpdateVariantBarcode($variantQid: String!, $barcode: String!, $barcodeType: String) {
    updateVariantBarcode(variantQid: $variantQid, barcode: $barcode, barcodeType: $barcodeType) {
        id
        qid
        identification {
            barcode
            barcodeType
        }
        updatedAt
    }
}
"""

# 🔟 التحقق من توفر SKU
CHECK_SKU_AVAILABILITY_MUTATION = """
mutation CheckSKUAvailability($sku: String!, $excludeQid: String) {
    checkSKUAvailability(sku: $sku, excludeQid: $excludeQid) {
        available
        message
        existingProduct {
            qid
            title
        }
    }
}
"""

# 1️⃣1️⃣ التحقق من توفر Barcode
CHECK_BARCODE_AVAILABILITY_MUTATION = """
mutation CheckBarcodeAvailability($barcode: String!, $excludeQid: String) {
    checkBarcodeAvailability(barcode: $barcode, excludeQid: $excludeQid) {
        available
        message
        existingProduct {
            qid
            title
        }
    }
}
"""

# 1️⃣2️⃣ تحديث تعريفات متعددة دفعة واحدة
BULK_UPDATE_PRODUCT_IDENTIFICATION_MUTATION = """
mutation BulkUpdateProductIdentification($updates: [ProductIdentificationUpdateInput!]!) {
    bulkUpdateProductIdentification(updates: $updates) {
        success
        message
        data {
            qid
            identification {
                sku
                barcode
                barcodeType
                hsCode
                countryOfOrigin
                mpn
            }
            updatedAt
        }
        errors {
            qid
            error
        }
    }
}
"""


# ============================================================
# 🚀 SERVICE CLASS - خدمة تعريف المنتج
# ============================================================

class ProductIdentificationService:
    """
    خدمة إدارة تعريف المنتجات
    تحتوي على جميع عمليات تحديث SKU، Barcode، HS Code، وغيرها
    """
    
    def __init__(self):
        self.client = QomrahGraphQLClient()
    
    # ============================================================
    # 🔍 CHECK AVAILABILITY - التحقق من التوفر
    # ============================================================
    
    def check_sku_availability(self, sku: str, exclude_qid: str = None) -> Dict:
        """
        التحقق من توفر SKU
        
        Args:
            sku: رقم SKU للتحقق
            exclude_qid: معرف المنتج المستثنى (للتحديث)
        
        Returns:
            Dict: {available: bool, message: str, existingProduct: dict}
        """
        variables = {"sku": sku}
        if exclude_qid:
            variables["excludeQid"] = exclude_qid
        
        result = self.client.execute_query(CHECK_SKU_AVAILABILITY_MUTATION, variables)
        return result.get('checkSKUAvailability', {}) if result else {}
    
    def check_barcode_availability(self, barcode: str, exclude_qid: str = None) -> Dict:
        """
        التحقق من توفر Barcode
        
        Args:
            barcode: الباركود للتحقق
            exclude_qid: معرف المنتج المستثنى (للتحديث)
        
        Returns:
            Dict: {available: bool, message: str, existingProduct: dict}
        """
        variables = {"barcode": barcode}
        if exclude_qid:
            variables["excludeQid"] = exclude_qid
        
        result = self.client.execute_query(CHECK_BARCODE_AVAILABILITY_MUTATION, variables)
        return result.get('checkBarcodeAvailability', {}) if result else {}
    
    # ============================================================
    # 📝 PRODUCT IDENTIFICATION - تعريف المنتج
    # ============================================================
    
    def update_product_identification(self, qid: str, sku: str = None,
                                      barcode: str = None,
                                      barcode_type: str = None,
                                      hs_code: str = None,
                                      country_of_origin: str = None,
                                      mpn: str = None) -> Optional[Dict]:
        """
        تحديث تعريف المنتج (جميع الحقول)
        
        Args:
            qid: معرف المنتج
            sku: رقم SKU
            barcode: الباركود
            barcode_type: نوع الباركود (EAN13, UPC, etc.)
            hs_code: رمز HS
            country_of_origin: بلد المنشأ
            mpn: رقم MPN
        
        Returns:
            Dict: بيانات التعريف المحدثة
        """
        identification = {}
        
        if sku is not None:
            identification["sku"] = sku
        if barcode is not None:
            identification["barcode"] = barcode
        if barcode_type is not None:
            identification["barcodeType"] = barcode_type
        if hs_code is not None:
            identification["hsCode"] = hs_code
        if country_of_origin is not None:
            identification["countryOfOrigin"] = country_of_origin
        if mpn is not None:
            identification["mpn"] = mpn
        
        if not identification:
            print("⚠️ لا توجد بيانات تعريف للتحديث")
            return None
        
        result = self.client.execute_query(
            UPDATE_PRODUCT_IDENTIFICATION_MUTATION,
            {"qid": qid, "identification": identification}
        )
        return result.get('updateProductIdentification') if result else None
    
    def update_product_sku(self, qid: str, sku: str) -> Optional[Dict]:
        """
        تحديث SKU للمنتج
        
        Args:
            qid: معرف المنتج
            sku: رقم SKU الجديد
        
        Returns:
            Dict: بيانات SKU المحدثة
        """
        # التحقق من توفر SKU
        availability = self.check_sku_availability(sku, qid)
        if not availability.get('available', True):
            print(f"⚠️ SKU '{sku}' غير متاح: {availability.get('message')}")
            return None
        
        result = self.client.execute_query(
            UPDATE_PRODUCT_SKU_MUTATION,
            {"qid": qid, "sku": sku}
        )
        return result.get('updateProductSKU') if result else None
    
    def update_product_barcode(self, qid: str, barcode: str,
                               barcode_type: str = None) -> Optional[Dict]:
        """
        تحديث Barcode للمنتج
        
        Args:
            qid: معرف المنتج
            barcode: الباركود الجديد
            barcode_type: نوع الباركود (EAN13, UPC, etc.)
        
        Returns:
            Dict: بيانات Barcode المحدثة
        """
        # التحقق من توفر Barcode
        availability = self.check_barcode_availability(barcode, qid)
        if not availability.get('available', True):
            print(f"⚠️ Barcode '{barcode}' غير متاح: {availability.get('message')}")
            return None
        
        variables = {"qid": qid, "barcode": barcode}
        if barcode_type:
            variables["barcodeType"] = barcode_type
        
        result = self.client.execute_query(UPDATE_PRODUCT_BARCODE_MUTATION, variables)
        return result.get('updateProductBarcode') if result else None
    
    def update_product_hs_code(self, qid: str, hs_code: str) -> Optional[Dict]:
        """
        تحديث HS Code للمنتج
        
        Args:
            qid: معرف المنتج
            hs_code: رمز HS الجديد
        
        Returns:
            Dict: بيانات HS Code المحدثة
        """
        result = self.client.execute_query(
            UPDATE_PRODUCT_HS_CODE_MUTATION,
            {"qid": qid, "hsCode": hs_code}
        )
        return result.get('updateProductHSCode') if result else None
    
    def update_product_country_of_origin(self, qid: str,
                                         country_of_origin: str) -> Optional[Dict]:
        """
        تحديث بلد المنشأ للمنتج
        
        Args:
            qid: معرف المنتج
            country_of_origin: بلد المنشأ الجديد
        
        Returns:
            Dict: بيانات بلد المنشأ المحدثة
        """
        result = self.client.execute_query(
            UPDATE_PRODUCT_COUNTRY_OF_ORIGIN_MUTATION,
            {"qid": qid, "countryOfOrigin": country_of_origin}
        )
        return result.get('updateProductCountryOfOrigin') if result else None
    
    def update_product_mpn(self, qid: str, mpn: str) -> Optional[Dict]:
        """
        تحديث MPN للمنتج
        
        Args:
            qid: معرف المنتج
            mpn: رقم MPN الجديد
        
        Returns:
            Dict: بيانات MPN المحدثة
        """
        result = self.client.execute_query(
            UPDATE_PRODUCT_MPN_MUTATION,
            {"qid": qid, "mpn": mpn}
        )
        return result.get('updateProductMPN') if result else None
    
    # ============================================================
    # 🎨 VARIANT IDENTIFICATION - تعريف الفاريانت
    # ============================================================
    
    def update_variant_identification(self, variant_qid: str,
                                     sku: str = None,
                                     barcode: str = None,
                                     barcode_type: str = None,
                                     hs_code: str = None,
                                     country_of_origin: str = None,
                                     mpn: str = None) -> Optional[Dict]:
        """
        تحديث تعريف الفاريانت
        
        Args:
            variant_qid: معرف الفاريانت
            sku: رقم SKU
            barcode: الباركود
            barcode_type: نوع الباركود
            hs_code: رمز HS
            country_of_origin: بلد المنشأ
            mpn: رقم MPN
        
        Returns:
            Dict: بيانات التعريف المحدثة
        """
        identification = {}
        
        if sku is not None:
            identification["sku"] = sku
        if barcode is not None:
            identification["barcode"] = barcode
        if barcode_type is not None:
            identification["barcodeType"] = barcode_type
        if hs_code is not None:
            identification["hsCode"] = hs_code
        if country_of_origin is not None:
            identification["countryOfOrigin"] = country_of_origin
        if mpn is not None:
            identification["mpn"] = mpn
        
        if not identification:
            print("⚠️ لا توجد بيانات تعريف للتحديث")
            return None
        
        result = self.client.execute_query(
            UPDATE_VARIANT_IDENTIFICATION_MUTATION,
            {"variantQid": variant_qid, "identification": identification}
        )
        return result.get('updateVariantIdentification') if result else None
    
    def update_variant_sku(self, variant_qid: str, sku: str) -> Optional[Dict]:
        """
        تحديث SKU للفاريانت
        
        Args:
            variant_qid: معرف الفاريانت
            sku: رقم SKU الجديد
        
        Returns:
            Dict: بيانات SKU المحدثة
        """
        # التحقق من توفر SKU (مع استبعاد الفاريانت نفسه)
        availability = self.check_sku_availability(sku, variant_qid)
        if not availability.get('available', True):
            print(f"⚠️ SKU '{sku}' غير متاح: {availability.get('message')}")
            return None
        
        result = self.client.execute_query(
            UPDATE_VARIANT_SKU_MUTATION,
            {"variantQid": variant_qid, "sku": sku}
        )
        return result.get('updateVariantSKU') if result else None
    
    def update_variant_barcode(self, variant_qid: str, barcode: str,
                               barcode_type: str = None) -> Optional[Dict]:
        """
        تحديث Barcode للفاريانت
        
        Args:
            variant_qid: معرف الفاريانت
            barcode: الباركود الجديد
            barcode_type: نوع الباركود
        
        Returns:
            Dict: بيانات Barcode المحدثة
        """
        # التحقق من توفر Barcode
        availability = self.check_barcode_availability(barcode, variant_qid)
        if not availability.get('available', True):
            print(f"⚠️ Barcode '{barcode}' غير متاح: {availability.get('message')}")
            return None
        
        variables = {"variantQid": variant_qid, "barcode": barcode}
        if barcode_type:
            variables["barcodeType"] = barcode_type
        
        result = self.client.execute_query(UPDATE_VARIANT_BARCODE_MUTATION, variables)
        return result.get('updateVariantBarcode') if result else None
    
    # ============================================================
    # 📦 BULK OPERATIONS - عمليات دفعة واحدة
    # ============================================================
    
    def bulk_update_product_identification(self, updates: List[Dict]) -> Dict:
        """
        تحديث تعريفات منتجات متعددة دفعة واحدة
        
        Args:
            updates: قائمة بالتحديثات [
                {
                    'qid': str,
                    'sku': str (optional),
                    'barcode': str (optional),
                    'barcodeType': str (optional),
                    'hsCode': str (optional),
                    'countryOfOrigin': str (optional),
                    'mpn': str (optional)
                }
            ]
        
        Returns:
            Dict: {success: bool, data: List, errors: List}
        """
        result = self.client.execute_query(
            BULK_UPDATE_PRODUCT_IDENTIFICATION_MUTATION,
            {"updates": updates}
        )
        
        if result:
            return result.get('bulkUpdateProductIdentification', {})
        return {'success': False, 'data': [], 'errors': []}
    
    # ============================================================
    # 🔄 SYNC OPERATIONS - عمليات المزامنة
    # ============================================================
    
    def sync_identification_from_data(self, qid: str, data: Dict) -> bool:
        """
        مزامنة بيانات التعريف من مصدر بيانات
        
        Args:
            qid: معرف المنتج
            data: بيانات المصدر {sku, barcode, hsCode, countryOfOrigin, mpn}
        
        Returns:
            bool: نجاح أو فشل العملية
        """
        try:
            success = True
            
            # تحديث SKU
            if 'sku' in data and data['sku']:
                if not self.update_product_sku(qid, data['sku']):
                    success = False
            
            # تحديث Barcode
            if 'barcode' in data and data['barcode']:
                if not self.update_product_barcode(
                    qid,
                    data['barcode'],
                    data.get('barcodeType')
                ):
                    success = False
            
            # تحديث HS Code
            if 'hsCode' in data and data['hsCode']:
                if not self.update_product_hs_code(qid, data['hsCode']):
                    success = False
            
            # تحديث بلد المنشأ
            if 'countryOfOrigin' in data and data['countryOfOrigin']:
                if not self.update_product_country_of_origin(qid, data['countryOfOrigin']):
                    success = False
            
            # تحديث MPN
            if 'mpn' in data and data['mpn']:
                if not self.update_product_mpn(qid, data['mpn']):
                    success = False
            
            return success
            
        except Exception as e:
            print(f"❌ خطأ في sync_identification_from_data: {e}")
            return False
    
    def generate_sku(self, prefix: str = "PRD", length: int = 8) -> str:
        """
        إنشاء SKU تلقائياً
        
        Args:
            prefix: بادئة SKU
            length: عدد الأرقام العشوائية
        
        Returns:
            str: SKU جديد
        """
        import random
        import string
        
        # إنشاء أرقام عشوائية
        numbers = ''.join(random.choices(string.digits, k=length))
        sku = f"{prefix}-{numbers}"
        
        # التحقق من عدم وجود SKU مكرر
        attempts = 0
        while attempts < 10:
            availability = self.check_sku_availability(sku)
            if availability.get('available', True):
                return sku
            # إنشاء SKU جديد
            numbers = ''.join(random.choices(string.digits, k=length))
            sku = f"{prefix}-{numbers}"
            attempts += 1
        
        # إذا فشل، أضف طابع زمني
        import time
        timestamp = str(int(time.time()))[-6:]
        return f"{prefix}-{timestamp}"


# ============================================================
# 🚀 SINGLETON INSTANCE
# ============================================================

product_ident = ProductIdentificationService()


# ============================================================
# 📋 EXPORTS - للاستخدام المباشر
# ============================================================

__all__ = [
    'UPDATE_PRODUCT_IDENTIFICATION_MUTATION',
    'UPDATE_PRODUCT_SKU_MUTATION',
    'UPDATE_PRODUCT_BARCODE_MUTATION',
    'UPDATE_PRODUCT_HS_CODE_MUTATION',
    'UPDATE_PRODUCT_COUNTRY_OF_ORIGIN_MUTATION',
    'UPDATE_PRODUCT_MPN_MUTATION',
    'UPDATE_VARIANT_IDENTIFICATION_MUTATION',
    'UPDATE_VARIANT_SKU_MUTATION',
    'UPDATE_VARIANT_BARCODE_MUTATION',
    'CHECK_SKU_AVAILABILITY_MUTATION',
    'CHECK_BARCODE_AVAILABILITY_MUTATION',
    'BULK_UPDATE_PRODUCT_IDENTIFICATION_MUTATION',
    'ProductIdentificationService',
    'product_ident'
]


# ============================================================
# 🧪 TEST - اختبار سريع (اختياري)
# ============================================================

if __name__ == "__main__":
    service = ProductIdentificationService()
    
    # اختبار إنشاء SKU تلقائي
    sku = service.generate_sku(prefix="TEST")
    print(f"✅ SKU جديد: {sku}")
    
    # اختبار التحقق من SKU
    # availability = service.check_sku_availability("TEST-12345678")
    # print(f"📊 توفر SKU: {availability}")
    
    print("✅ Product Identification Service ready!")
