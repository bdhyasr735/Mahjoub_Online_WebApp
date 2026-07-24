# coding: utf-8
# 📂 apps/services/product_mutations.py

from typing import Dict, List, Optional
import base64
import logging
from apps.services.product_mapping_service import product_mapping

logger = logging.getLogger(__name__)


class ProductMutations:
    """تحويرات المنتجات في قمرة"""

    def __init__(self, client):
        self.client = client

    def upload_image(self, image_data: bytes, filename: str) -> Optional[str]:
        """رفع صورة"""
        try:
            ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpeg'
            b64 = base64.b64encode(image_data).decode('utf-8')

            mutation = """
            mutation ($file: String!, $filename: String!) {
                uploadFile(file: $file, filename: $filename) {
                    success message data { fileUrl _id }
                }
            }
            """
            variables = {"file": f"data:image/{ext};base64,{b64}", "filename": filename}
            result = self.client.execute_query(mutation, variables)
            return result.get('uploadFile', {}).get('data', {}).get('fileUrl')
        except Exception as e:
            logger.error(f"❌ رفع الصورة: {e}")
            return None

    def create_product(self, title: str, description: str = "", price: float = 0.0,
                       status: str = "DRAFT", images: List[str] = None,
                       supplier_id: int = None, **kwargs) -> Dict:
        """إنشاء منتج"""
        mutation = """
        mutation ($input: CreateProductInput!) {
            createProduct(input: $input) { id qid title slug price status description createdAt }
        }
        """
        input_data = {"title": title, "description": description, "price": price, "status": status}
        if images:
            input_data["images"] = images
        if kwargs.get('weight'):
            input_data["weight"] = kwargs['weight']
        if kwargs.get('sku'):
            input_data["sku"] = kwargs['sku']

        result = self.client.execute_query(mutation, {"input": input_data})
        data = result.get('createProduct', {}) if result else {}

        if data and supplier_id:
            from datetime import datetime
            product_mapping.add_mapping(
                product_qid=data.get('qid'),
                supplier_id=supplier_id,
                internal_notes=f"تم الإنشاء {datetime.now()}"
            )

        return {'success': bool(data), 'qid': data.get('qid'), 'data': data}

    def update_product_info(self, qid: str, title: str = None,
                            description: str = None, status: str = None) -> bool:
        """تحديث معلومات المنتج"""
        input_data = {}
        if title:
            input_data["title"] = title
        if description:
            input_data["description"] = description
        if status:
            input_data["status"] = status
        if not input_data:
            return False

        mutation = """
        mutation ($qid: String!, $input: UpdateProductInfoInput!) {
            updateProductInfo(qid: $qid, input: $input) { id qid title description status }
        }
        """
        result = self.client.execute_query(mutation, {"qid": qid, "input": input_data})
        return bool(result and result.get('updateProductInfo'))

    def update_product_pricing(self, qid: str, price: float, compare_at_price: float = None) -> bool:
        """تحديث السعر"""
        mutation = """
        mutation ($qid: String!, $price: Float!, $compareAtPrice: Float) {
            updateProductPricing(qid: $qid, price: $price, compareAtPrice: $compareAtPrice) { id qid price }
        }
        """
        variables = {"qid": qid, "price": price}
        if compare_at_price:
            variables["compareAtPrice"] = compare_at_price
        result = self.client.execute_query(mutation, variables)
        return bool(result and result.get('updateProductPricing'))

    def update_product_status(self, qid: str, status: str) -> bool:
        """تحديث الحالة"""
        mutation = """
        mutation ($qid: String!, $status: String!) {
            updateProductStatus(qid: $qid, status: $status) { id qid status }
        }
        """
        result = self.client.execute_query(mutation, {"qid": qid, "status": status})
        return bool(result and result.get('updateProductStatus'))

    def update_product_images(self, qid: str, images: List[str]) -> bool:
        """تحديث الصور"""
        mutation = """
        mutation ($qid: String!, $images: [String!]!) {
            updateProductImages(qid: $qid, images: $images) { id qid images }
        }
        """
        result = self.client.execute_query(mutation, {"qid": qid, "images": images})
        return bool(result and result.get('updateProductImages'))

    def update_product_weight(self, qid: str, weight: float, unit: str = 'kg') -> bool:
        """تحديث الوزن"""
        mutation = """
        mutation ($qid: String!, $weight: Float!, $unit: String!) {
            updateProductWeight(qid: $qid, weight: $weight, unit: $unit) { id qid weight }
        }
        """
        result = self.client.execute_query(mutation, {"qid": qid, "weight": weight, "unit": unit})
        return bool(result and result.get('updateProductWeight'))

    def delete_product(self, qid: str, delete_mapping: bool = True) -> bool:
        """حذف منتج"""
        mutation = """
        mutation ($qid: String!) { deleteProduct(qid: $qid) }
        """
        result = self.client.execute_query(mutation, {"qid": qid})
        if result and result.get('deleteProduct') is True:
            if delete_mapping:
                product_mapping.delete_mapping(qid)
            return True
        return False
