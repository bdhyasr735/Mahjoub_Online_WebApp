# 📂 tests/test_csrf.py
import unittest
import json
from apps import create_app

class CSRFSecurityTestCase(unittest.TestCase):
    def setUp(self):
        """إعداد بيئة الاختبار وتفعيل حماية CSRF"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = True
        self.client = self.app.test_client()

    def test_01_get_route_returns_csrf_header(self):
        """1. التحقق من أن السيرفر يرفق الرمز تلقائياً في ترويسات الاستجابة"""
        response = self.client.get('/')
        csrf_token = response.headers.get('X-CSRF-Token')
        
        self.assertIsNotNone(csrf_token, "⚠️ فشل الاختبار: السيرفر لم يرسل X-CSRF-Token في الهيدر.")
        print(f"\n✅ [PASS]: تم استقبال الرمز من السيرفر: {csrf_token[:15]}...")

    def test_02_post_without_csrf_rejected(self):
        """2. التحقق من حظر طلبات POST غير المستثناة بـ status 400 عند غياب الرمز"""
        response = self.client.post(
            '/auth/login', 
            data={'username': 'test_user', 'password': '123'},
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        
        self.assertIn(response.status_code, [400, 403], "⚠️ فشل الاختبار: تم قبول الطلب بدون رمز CSRF!")
        print("✅ [PASS]: تم حظر الطلب المحمي بنجاح عند غياب الرمز.")

    def test_03_whatsapp_exempt_from_csrf(self):
        """3. التحقق من أن مسارات الواتساب مستثناة تماماً لضمان وصول الـ Webhook"""
        response = self.client.post(
            '/api/whatsapp/test-send',
            data=json.dumps({'phone': '967779077746'}),
            content_type='application/json'
        )
        
        self.assertNotIn(response.status_code, [400, 403], "⚠️ فشل الاختبار: مسار الواتساب محظور بـ CSRF بالخطأ!")
        print("✅ [PASS]: تم التأكد من استثناء خدمات الواتساب من حماية CSRF.")

    def test_04_post_with_valid_csrf_accepted(self):
        """4. التحقق من قبول الطلب المحمي عند استخراج الرمز وإرفاقه بالترويسة"""
        with self.client as c:
            get_res = c.get('/')
            csrf_token = get_res.headers.get('X-CSRF-Token')

            post_res = c.post(
                '/auth/login',
                headers={'X-CSRF-Token': csrf_token},
                data={'username': 'test_user', 'password': '123'}
            )
            
            self.assertNotIn(post_res.status_code, [400, 403], f"⚠️ فشل الاختبار: تم رفض الرمز الصحيح (Status: {post_res.status_code})")
            print("✅ [PASS]: تم التحقق من الرمز وقبول الطلب بنجاح.")

if __name__ == '__main__':
    unittest.main()
