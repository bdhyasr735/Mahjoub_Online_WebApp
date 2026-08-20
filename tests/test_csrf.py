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
        """2. التحقق من رفض طلبات POST المحمية فوراً بحالة 400 عند غياب الرمز"""
        # محاولة إرسال طلب بدون CSRF Token
        response = self.client.post(
            '/test_csrf_check', 
            data=json.dumps({'message': 'اختبار بدون رمز'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400, "⚠️ فشل الاختبار: تم قبول الطلب بدون رمز CSRF!")
        print("✅ [PASS]: تم حظر الطلب غير المحمي بنجاح (HTTP 400 Bad Request).")

    def test_03_post_with_valid_csrf_accepted(self):
        """3. التحقق من قبول الطلب عند استخراج الرمز واستخدامه بالترويسة"""
        # أ) الحصول على الرمز
        get_res = self.client.get('/')
        csrf_token = get_res.headers.get('X-CSRF-Token')

        # ب) إرسال الطلب مع إرفاق الرمز في الهيدر
        post_res = self.client.post(
            '/admin/graphql',
            headers={
                'X-CSRF-Token': csrf_token,
                'Content-Type': 'application/json'
            },
            data=json.dumps({'query': '{ __typename }'})
        )
        
        # المسارات المستثناة أو المسارات المحمية بـ Token مقبول تعيد 200
        self.assertIn(post_res.status_code, [200, 302], f"⚠️ فشل الاختبار: الرمز المرفق تم رفضه (Status: {post_res.status_code})")
        print("✅ [PASS]: تم التحقق من الرمز وقبول الطلب بنجاح.")

if __name__ == '__main__':
    unittest.main()
