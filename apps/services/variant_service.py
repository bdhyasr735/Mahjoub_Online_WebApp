from typing import Dict, Any, Optional, List
import os
from .graphql_client import GraphQLClient


class VariantService:
    def __init__(self, client: GraphQLClient):
        self.client = client
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.query_file_path = os.path.join(current_dir, 'variant_queries.graphql')
        
        try:
            with open(self.query_file_path, 'r', encoding='utf-8') as f:
                self.queries_content = f.read()
        except FileNotFoundError:
            print(f"⚠️ [VariantService]: لم يتم العثور على ملف الاستعلامات")
            self.queries_content = ""

    def _extract_query(self, query_name: str) -> str:
        """استخراج استعلام معين من ملف الاستعلامات"""
        if not self.queries_content:
            return ""
        
        lines = self.queries_content.split('\n')
        result = []
        found = False
        brace_count = 0
        
        for line in lines:
            if f"query {query_name}" in line or f"mutation {query_name}" in line:
                found = True
            
            if found:
                result.append(line)
                brace_count += line.count('{') - line.count('}')
                if brace_count == 0 and len(result) > 1:
                    break
        
        return '\n'.join(result)

    def get_all_options_for_product(self, qid: str) -> List[Dict[str, Any]]:
        """جلب جميع خيارات المنتج الأساسية"""
        query = self._extract_query("FindAllOptionsForProduct")
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
        """جلب جميع المتغيرات الخاصة بالمنتج"""
        query = self._extract_query("FindAllVariantsByProductId")
        variables = {"productId": product_id, "getAllVariantsInput": pagination_input or {}}
        try:
            data = self.client.execute(query, variables, operation_name="FindAllVariantsByProductId")
            return data.get('findAllVariantsByProductId', {}).get('data', []) if data else []
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في جلب المتغيرات للمنتج {product_id}: {e}")
            return []

    def get_by_id(self, variant_id: str) -> Optional[Dict[str, Any]]:
        """جلب متغير محدد"""
        query = self._extract_query("FindVariantById")
        variables = {"id": variant_id}
        try:
            data = self.client.execute(query, variables, operation_name="FindVariantById")
            return data.get('findVariantById', {}).get('data') if data else None
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في جلب المتغير {variant_id}: {e}")
            return None

    def update_pricing(self, variant_id: str, pricing_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """تحديث أسعار المتغير"""
        query = self._extract_query("UpdateVariantPricing")
        variables = {"variantId": variant_id, "pricing": pricing_data}
        try:
            data = self.client.execute(query, variables, operation_name="UpdateVariantPricing")
            return data.get('updateVariantPricing', {}).get('data') if data else None
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في تحديث سعر المتغير {variant_id}: {e}")
            return None

    def update_media(self, variant_id: str, media: List[str]) -> Optional[Dict[str, Any]]:
        """تحديث وسائط المتغير"""
        query = self._extract_query("UpdateVariantMedia")
        variables = {"variantId": variant_id, "media": media}
        try:
            data = self.client.execute(query, variables, operation_name="UpdateVariantMedia")
            return data.get('updateVariantMedia', {}).get('data') if data else None
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في تحديث وسائط المتغير {variant_id}: {e}")
            return None

    def delete(self, variant_id: str) -> bool:
        """حذف متغير"""
        query = self._extract_query("RemoveVariantById")
        variables = {"id": variant_id}
        try:
            data = self.client.execute(query, variables, operation_name="RemoveVariantById")
            return data.get('removeVariantById', False) if data else False
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في حذف المتغير {variant_id}: {e}")
            return False

    def bulk_update(self, bulk_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """التحديث الجماعي للمتغيرات"""
        query = self._extract_query("BulkVariantUpdate")
        variables = {"bulkUpdateVariantsInput": bulk_input}
        try:
            data = self.client.execute(query, variables, operation_name="BulkVariantUpdate")
            return data.get('bulkVariantUpdate', {}).get('data', []) if data else []
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في التحديث الجماعي للمتغيرات: {e}")
            return []

    # ✅ دالة تحديث الكمية (مضافة حديثاً)
    def update_quantity(self, variant_id: str, quantity: int) -> Optional[Dict[str, Any]]:
        """تحديث كمية المتغير"""
        query = self._extract_query("UpdateVariantQuantity")
        variables = {"variantId": variant_id, "quantity": quantity}
        try:
            data = self.client.execute(query, variables, operation_name="UpdateVariantQuantity")
            return data.get('updateVariantQuantity', {}).get('data') if data else None
        except Exception as e:
            print(f"❌ [VariantService]: خطأ في تحديث كمية المتغير {variant_id}: {e}")
            return None
