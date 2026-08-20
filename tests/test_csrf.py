# 📂 tests/test_csrf.py
import unittest
import json
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
        """قراءة المفاتيح من config.py أو استخدام قيم الاختبار المباشرة"""
        with self.app.app_context():
            # يقرأ من config.py الخاص بـ Flask، وفي حال عدم وجوده يضع المفتاح الحقيقي للاختبار
            token = self.app.config.get('WHATSAPP_TOKEN') or "ضع_التوكن_الخاص_بـMeta_هنا"
            phone_id = self.app.config.get('WHATSAPP_PHONE_ID') or "ضع_Phone_Number_ID_هنا"
            target_phone = "967779077746"

            url = f"https://graph.facebook.com/v19.0/{phone_id}/messages"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": target_phone,
                "type": "template",
                "template": {
                    "name": "hello_world",
                    "language": {"code": "en_US"}
                }
            }

            res = requests.post(url, json=payload, headers=headers)
            print(f"\n📩 [Meta Status]: {res.status_code}")
            print(f"📩 [Meta Response]: {res.text}\n")

if __name__ == '__main__':
    unittest.main()
