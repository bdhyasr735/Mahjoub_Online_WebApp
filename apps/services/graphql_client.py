import os
import json
import requests


class GraphQLClient:

    def __init__(self, endpoint=None, token=None):
        # ⚠️ الرابط الافتراضي أصبح يتطابق مع ما تم وضعه في Render
        # أولوية التعيين: 1. الوسيط (endpoint) 2. متغير البيئة 3. القيمة الافتراضية
        self.endpoint = endpoint or os.getenv(
            "QUMRA_ENDPOINT", "https://api.qumra.cloud/graphql"  # الرابط الصحيح مع النقطة
        )
        
        # جلب التوكن من متغير البيئة، مع إزالة أي مسافات إضافية
        raw_token = token or os.getenv(
            "QUMRA_TOKEN", "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"
        )
        self.token = raw_token.strip() if raw_token else ""

    def execute(self, query: str, variables: dict = None):
        # التحقق من وجود التوكن حتى لا نرسل طلباً فارغاً
        if not self.token:
            print("❌ [Qumra Error] لم يتم العثور على توكن المصادقة (QUMRA_TOKEN).")
            return None

        # ✅ إعداد الرؤوس (Headers) بالشكل الصحيح
        headers = {
            "Content-Type": "application/json",  # يمنع خطأ CSRF
            "Authorization": f"Bearer {self.token}",  # الكود يضيف Bearer تلقائياً
        }

        # تحضير الحمولة (Payload) بصيغة JSON
        payload = {"query": query, "variables": variables or {}}

        try:
            # ⚠️ استخدام json= بدلاً من data= لضمان إرسال JSON صحيح
            response = requests.post(
                self.endpoint, json=payload, headers=headers, timeout=15
            )

            # معالجة الأخطاء الشائعة من الخادم
            if response.status_code in (401, 403, 500):
                error_detail = ""
                try:
                    error_json = response.json()
                    if "errors" in error_json:
                        error_detail = error_json["errors"]
                    else:
                        error_detail = error_json
                except:
                    error_detail = response.text[:200]

                print(
                    f"❌ [Qumra Response Error] HTTP {response.status_code}:"
                    f" {error_detail}"
                )
                return None

            # رفع أي خطأ HTTP غير متوقع (مثل 404 أو 502)
            response.raise_for_status()
            
            result = response.json()

            # التحقق من وجود أخطاء في استجابة GraphQL نفسها
            if "errors" in result:
                print(f"❌ [Qumra GraphQL Error]: {result['errors']}")
                return None

            # إرجاع البيانات فقط في حال النجاح
            return result.get("data")

        # معالجة استثناءات الشبكة بشكل منفصل للحصول على رسائل واضحة
        except requests.exceptions.Timeout:
            print("❌ [Qumra Request Exception]: انتهت مهلة الاتصال بالخادم (Timeout).")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ [Qumra Request Exception]: فشل الاتصال بالخادم (Connection Error). تحقق من الرابط.")
            return None
        except requests.exceptions.HTTPError as http_err:
            print(f"❌ [Qumra HTTP Error]: {http_err}")
            return None
        except Exception as e:
            print(f"❌ [Qumra Request Exception]: {e}")
            return None
