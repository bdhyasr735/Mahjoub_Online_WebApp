# 📂 tests/test_csrf.py
import unittest
import json
from apps import create_app

class CSRFSecurityTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = True
        self.client = self.app.test_client()

    def test_01_get_route_returns_csrf_header(self):
        """التحقق من إرفاق رمز CSRF في الترويسة"""
        response = self.client.get('/')
        csrf_token = response.headers.get('X-CSRF-Token')
        self.assertIsNotNone(csrf_token, "⚠️ لم يتم استقبال X-CSRF-Token")
        print(f"\n✅ [CSRF Header]: {csrf_token[:15]}...")

    def test_02_post_without_csrf_rejected(self):
        """حظر طلبات POST العادية عند غياب الرمز"""
        response = self.client.post(
            '/auth/login', 
            data={'username': 'test', 'password': '123'}
        )
        self.assertIn(response.status_code, [400, 403], "⚠️ تم قبول طلب غير محمي!")
        print("✅ [Protected Route]: تم حظر الطلب المحمي بنجاح.")

    def test_03_whatsapp_exempt_from_csrf(self):
        """تأكيد استثناء مسارات الواتساب للرقم 779077746 وسيرفر Meta"""
        response = self.client.post(
            '/api/whatsapp/test-send',
            data=json.dumps({'phone': '967779077746'}),
            content_type='application/json'
        )
        self.assertNotIn(response.status_code, [400, 403], "⚠️ مسار الواتساب محظور بـ CSRF!")
        print("✅ [WhatsApp Route]: مستثنى بنجاح وتعمل الإشارات دون عائق.")

if __name__ == '__main__':
    unittest.main()
