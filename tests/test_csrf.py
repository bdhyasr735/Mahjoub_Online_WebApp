# 📂 tests/test_csrf.py
import unittest
import json
from apps import create_app
from apps.whatsapp_service.whatsapp_api import send_whatsapp_text

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

    def test_02_post_without_csrf_rejected(self):
        """حظر طلبات POST العادية عند غياب الرمز"""
        response = self.client.post(
            '/auth/login', 
            data={'username': 'test', 'password': '123'}
        )
        self.assertIn(response.status_code, [400, 403], "⚠️ تم قبول طلب غير محمي!")

    def test_03_trigger_whatsapp_send_on_upload(self):
        """إرسال رسالة الواتساب للرقم 779077746 فور رفع الملف وتشغيل السيرفر"""
        with self.app.app_context():
            test_msg = (
                "🏛️ *محجوب أونلاين*\n\n"
                "تم رفع الملف وتشغيل الاختبار بنجاح! هذه الرسالة تأكيد لوصول الإشعارات إلى الرقم (779077746). ✅"
            )
            res, status_code = send_whatsapp_text('967779077746', test_msg)
            print(f"\n📩 [WhatsApp Auto-Send Result]: Status {status_code} -> {res}")
            
            # التأكد من قبول Meta لطلب الإرسال
            self.assertEqual(status_code, 200, f"⚠️ فشل إرسال الواتساب: {res}")

if __name__ == '__main__':
    unittest.main()
