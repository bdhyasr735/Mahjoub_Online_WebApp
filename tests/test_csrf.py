# 📂 tests/test_csrf.py
import unittest
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
        self.assertIsNotNone(csrf_token)

    def test_02_post_without_csrf_rejected(self):
        response = self.client.post('/auth/login', data={'username': 'test', 'password': '123'})
        self.assertIn(response.status_code, [400, 403])

    def test_03_trigger_whatsapp_send_on_upload(self):
        """إرسال رسالة نصية مباشرة للرقم 779077746"""
        with self.app.app_context():
            token = self.app.config.get('WHATSAPP_ACCESS_TOKEN')
            phone_id = self.app.config.get('WHATSAPP_PHONE_NUMBER_ID')
            api_version = self.app.config.get('WHATSAPP_API_VERSION', 'v20.0')
            target_phone = "967779077746"

            if not token or not phone_id:
                print("❌ [Error]: المتغيرات مفقودة في البيئة الحالية.")
                return

            url = f"https://graph.facebook.com/{api_version}/{phone_id}/messages"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # 🎯 تم التغيير إلى رسالة نصية عادية وبنص مخصص
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": target_phone,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": "🏛️ *محجوب أونلاين*\n\nتم رفع الملف وتشغيل الاختبارات بنجاح! هذه الرسالة تأكيد لوصول الإشعارات المباشرة إلى رقمك. ✅"
                }
            }

            res = requests.post(url, json=payload, headers=headers)
            print(f"\n📩 [Meta Status Code]: {res.status_code}")
            print(f"📩 [Meta API Response]: {res.text}\n")

if __name__ == '__main__':
    unittest.main()
