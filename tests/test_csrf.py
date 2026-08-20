# 📂 tests/test_csrf.py
import unittest
import json
import os
import requests
from apps import create_app

class CSRFSecurityTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = True
        self.client = self.app.test_client()

    def test_01_get_route_returns_csrf_header(self):
        response = self.client.get('/')
        csrf_token = response.headers.get('X-CSRF-Token')
        self.assertIsNotNone(csrf_token, "⚠️ لم يتم استقبال X-CSRF-Token")

    def test_02_post_without_csrf_rejected(self):
        response = self.client.post(
            '/auth/login', 
            data={'username': 'test', 'password': '123'}
        )
        self.assertIn(response.status_code, [400, 403], "⚠️ تم قبول طلب غير محمي!")

    def test_03_trigger_whatsapp_send_on_upload(self):
        """إرسال رسالة باستخدام Template ومروراً عبر Meta مباشرة"""
        token = os.environ.get('WHATSAPP_TOKEN') or self.app.config.get('WHATSAPP_TOKEN')
        phone_id = os.environ.get('WHATSAPP_PHONE_ID') or self.app.config.get('WHATSAPP_PHONE_ID')
        target_phone = "967779077746"

        print(f"\n🔍 [Check] Phone ID: {phone_id} | Token Present: {bool(token)}")

        url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # استخدام قالب hello_world الرسمي من Meta لتجاوز نافذة الـ 24 ساعة
        payload = {
            "messaging_product": "whatsapp",
            "to": target_phone,
            "type": "template",
            "template": {
                "name": "hello_world",
                "language": {"code": "en_US"}
            }
        }

        try:
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            res_data = res.json()
            print(f"\n📩 [Meta API Status]: {res.status_code}")
            print(f"📩 [Meta API Response]: {json.dumps(res_data, ensure_ascii=False, indent=2)}\n")
            
            # التأكد من صحة الاستجابة
            self.assertEqual(res.status_code, 200, f"خطأ Meta: {res_data}")
        except Exception as e:
            print(f"\n❌ [Connection Error]: {str(e)}\n")
            raise e

if __name__ == '__main__':
    unittest.main()
