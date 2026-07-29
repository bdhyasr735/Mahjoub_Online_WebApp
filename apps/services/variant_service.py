from typing import Dict, Any, Optional, List
from .graphql_client import GraphQLClient


class VariantService:
    def __init__(self, client: GraphQLClient):
        self.client = client

    def get_all_options_for_product(self, qid: str) -> List[Dict[str, Any]]:
        """
        جلب جميع خيارات المنتج الأساسية مع التأكد من سلامة هيكلة القيم وتجنب أي خطأ تكرار
        """
        query = """
        query FindAllOptionsForProduct($qid: String!) {
            findAllOptionsForProduct(qid: $qid) {
                data {
                    qid
                    name
                    values {
                        option
                        label
                        sortOrder
                    }
                }
            }
        }
        """
        variables = {"qid": qid}
        try:
            result = self.client.execute(query, variables, operation_name="FindAllOptionsForProduct")
            options_data = result.get('findAllOptionsForProduct', {}).get('data', []) if result else []
            
            cleaned_options = []
            for opt in options_data:
                if isinstance(opt, dict):
                    vals = opt.get('values', [])
                    if callable(vals) or not isinstance(vals, list):
                        vals = []
                    cleaned_options.append({
                        "qid": opt.get('qid'),
                        "name": opt.get('name'),
                        "values": vals
                    })
            return cleaned_options
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في جلب خيارات المنتج {qid}: {e}")
            return []

    def get_by_product(self, product_id: str, pagination_input: Optional[Dict] = None) -> List[Dict[str, Any]]:
        """
        جلب جميع المتغيرات الخاصة بالمنتج مع خياراتها، كمياتها، وأسعارها
        """
        query = """
        query FindAllVariantsByProductId($productId: String!, $getAllVariantsInput: GetAllVariantsInput) {
            findAllVariantsByProductId(productId: $productId, getAllVariantsInput: $getAllVariantsInput) {
                data {
                    qid
                    sku
                    barcode
                    quantity
                    position
                    isActive
                    isAvailable
                    pricing {
                        price
                        compareAtPrice
                        originalPrice
                    }
                    options {
                        name
                        value
                    }
                }
            }
        }
        """
        variables = {"productId": product_id, "getAllVariantsInput": pagination_input or {}}
        try:
            data = self.client.execute(query, variables, operation_name="FindAllVariantsByProductId")
            return data.get('findAllVariantsByProductId', {}).get('data', []) if data else []
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في جلب المتغيرات للمنتج {product_id}: {e}")
            return []

    def get_by_id(self, variant_id: str) -> Optional[Dict[str, Any]]:
        """
        جلب متغير محدد بواسطة المعرف (id)
        """
        query = """
        query FindVariantById($id: String!) {
            findVariantById(id: $id) {
                data {
                    qid
                    sku
                    quantity
                }
            }
        }
        """
        variables = {"id": variant_id}
        try:
            data = self.client.execute(query, variables, operation_name="FindVariantById")
            return data.get('findVariantById', {}).get('data') if data else None
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في جلب المتغير {variant_id}: {e}")
            return None

    def update_pricing(self, variant_id: str, pricing_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        تحديث أسعار المتغير باستخدام كائن pricing الصحيح
        """
        query = """
        mutation UpdateVariantPricing($variantId: String!, $pricing: UpdateVariantPricingInput!) {
            updateVariantPricing(variantId: $variantId, pricing: $pricing) {
                data {
                    qid
                }
            }
        }
        """
        variables = {"variantId": variant_id, "pricing": pricing_data}
        try:
            data = self.client.execute(query, variables, operation_name="UpdateVariantPricing")
            return data.get('updateVariantPricing', {}).get('data') if data else None
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في تحديث سعر المتغير {variant_id}: {e}")
            return None

    def update_media(self, variant_id: str, media: List[str]) -> Optional[Dict[str, Any]]:
        """
        تحديث وسائط المتغير
        """
        query = """
        mutation UpdateVariantMedia($variantId: String!, $media: [String!]!) {
            updateVariantMedia(variantId: $variantId, media: $media) {
                data {
                    qid
                }
            }
        }
        """
        variables = {"variantId": variant_id, "media": media}
        try:
            data = self.client.execute(query, variables, operation_name="UpdateVariantMedia")
            return data.get('updateVariantMedia', {}).get('data') if data else None
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في تحديث وسائط المتغير {variant_id}: {e}")
            return None

    def delete(self, variant_id: str) -> bool:
        """
        حذف متغير بواسطة المعرف id
        """
        query = """
        mutation RemoveVariantById($id: String!) {
            removeVariantById(id: $id)
        }
        """
        variables = {"id": variant_id}
        try:
            data = self.client.execute(query, variables, operation_name="RemoveVariantById")
            return data.get('removeVariantById', False) if data else False
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في حذف المتغير {variant_id}: {e}")
            return False

    def bulk_update(self, bulk_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        التحديث الجماعي للمتغيرات باستخدام المدخل الصحيح bulkUpdateVariantsInput
        """
        query = """
        mutation BulkVariantUpdate($bulkUpdateVariantsInput: BulkUpdateVariantsInput!) {
            bulkVariantUpdate(bulkUpdateVariantsInput: $bulkUpdateVariantsInput) {
                data {
                    qid
                }
            }
        }
        """
        variables = {"bulkUpdateVariantsInput": bulk_input}
        try:
            data = self.client.execute(query, variables, operation_name="BulkVariantUpdate")
            return data.get('bulkVariantUpdate', {}).get('data', []) if data else []
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في التحديث الجماعي للمتغيرات: {e}")
            return []
