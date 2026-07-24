# coding: utf-8
# 📂 apps/services/product_sync_service.py

"""
الخدمة الأساسية لمزامنة المنتجات - تجمع الاستعلامات والتحويرات
"""

from apps.services.graphql_client import QomrahGraphQLClient
from apps.services.product_queries import ProductQueries
from apps.services.product_mutations import ProductMutations


class ProductSyncService:
    """خدمة مزامنة المنتجات الموحدة"""

    def __init__(self):
        self.client = QomrahGraphQLClient()
        self.queries = ProductQueries(self.client)
        self.mutations = ProductMutations(self.client)

    # ===== استعلامات =====
    def fetch_products(self, **kwargs):
        return self.queries.fetch_products(**kwargs)

    def fetch_product_by_qid(self, qid):
        return self.queries.fetch_product_by_qid(qid)

    # ===== تحويرات =====
    def create_product(self, **kwargs):
        return self.mutations.create_product(**kwargs)

    def update_product_info(self, qid, **kwargs):
        return self.mutations.update_product_info(qid, **kwargs)

    def update_product_pricing(self, qid, price, **kwargs):
        return self.mutations.update_product_pricing(qid, price, **kwargs)

    def update_product_status(self, qid, status):
        return self.mutations.update_product_status(qid, status)

    def update_product_images(self, qid, images):
        return self.mutations.update_product_images(qid, images)

    def update_product_weight(self, qid, weight, **kwargs):
        return self.mutations.update_product_weight(qid, weight, **kwargs)

    def delete_product(self, qid, **kwargs):
        return self.mutations.delete_product(qid, **kwargs)

    def upload_image(self, image_data, filename, **kwargs):
        return self.mutations.upload_image(image_data, filename, **kwargs)


# ============================================================
# 🚀 INSTANCE
# ============================================================

product_sync = ProductSyncService()
