# coding: utf-8
# 📂 apps/utils/bridge_engine.py - محرك الربط الآلي (Mahjoub Bridge Engine)

import requests
import json
from config import Config

class QumraBridgeEngine:
    def __init__(self):
        # نقطة الاتصال المعتمدة من لوحة تحكم قمرة
        self.endpoint = "https://mahjoub.online/admin/graphql"
        # التوثيق باستخدام مفتاح الربط الموجود في إعدادات التطبيق
        self.headers = {
            "Authorization": f"Bearer {Config.QUMRA_API_KEY}",
            "Content-Type": "application/json"
        }

    def execute_query(self, query, variables=None):
        """
        تنفيذ استعلام GraphQL وإرساله إلى منصة قمرة.
        query: نص الـ Mutation أو Query الخاص بـ GraphQL.
        variables: المتغيرات (مثل بيانات المنتج أو المتغيرات الخاصة به).
        """
        payload = {
            "query": query,
            "variables": variables or {}
        }
        
        try:
            response = requests.post(
                self.endpoint, 
                json=payload, 
                headers=self.headers,
                timeout=10 # حماية لضمان عدم تعليق المصنع
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            # توثيق الخطأ برمجياً للتعامل معه في سجلات المصنع
            print(f"⚠️ Bridge Engine Error: {e}")
            return {"errors": str(e)}

    def map_product_to_qumra(self, data):
        """
        محول البيانات (Mapper): يحول القالب الخاص بك إلى هيكل قمرة المطلوب.
        """
        # هنا سيتم صياغة الـ Mutation الذي يطابق هيكل البيانات المذكور في خطتك
        mutation = """
        mutation CreateProduct($input: ProductInput!) {
            createProduct(input: $input) {
                id
                name
            }
        }
        """
        # تجهيز المتغيرات بما يتوافق مع الـ Schema الخاص بقمرة
        variables = {
            "input": {
                "name": data.get('title'),
                "description": data.get('description'),
                "price": float(data.get('price', 0)),
                "quantity": int(data.get('quantity', 0)),
                # إضافة التعامل مع الـ Variants هنا لاحقاً
            }
        }
        return self.execute_query(mutation, variables)
