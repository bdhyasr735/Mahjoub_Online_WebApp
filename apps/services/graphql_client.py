import os
import json
import requests


class GraphQLClient:

    def __init__(self, endpoint=None, token=None):
        # ⚠️ تم تعديل الرابط الافتراضي ليتطابق مع الـ URL الظاهر في سجلاتك
        # إذا كان الرابط الصحيح هو api.qumra.cloud، قم بتعديله في متغير البيئة QUMRA_ENDPOINT
        self.endpoint = endpoint or os.getenv(
            "QUMRA_ENDPOINT", "https://apiqumra.cloud/graphql"
        )
        
        raw_token = token or os.getenv(
            "QUMRA_TOKEN", "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"
        )
        self.token = raw_token.strip() if raw_token else ""

    def execute(self, query: str, variables: dict = None):
        # ✅ التأكد من وجود التوكن، وإلا يعطي خطأ واضحاً بدلاً من فشل صامت
        if not self.token:
            print("❌ [Qumra Error] لم يتم العثور على توكن المصادقة (QUMRA_TOKEN).")
            return None

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }

        payload = {"query": query, "variables": variables or {}}

        try:
            response = requests.post(
                self.endpoint, json=payload, headers=headers, timeout=15
            )

            # عرض تفاصيل الاستجابة في حال حدوث خطأ في المصادقة أو الخادم
            if response.status_code in (401, 403, 500):
                error_detail = ""
                try:
                    error_json = response.json()
                    if "errors" in error_json:
                        error_detail = error_json["errors"]
                    else:
                        error_detail = error_json
                except:
                    error_detail = response.text[:200]  # اقتطاع النص الطويل

                print(
                    f"❌ [Qumra Response Error] HTTP {response.status_code}:"
                    f" {error_detail}"
                )
                return None

            # إذا كان الـ response غير ناجح (مثل 404 أو 502)
            response.raise_for_status()
            
            result = response.json()

            # التحقق من وجود أخطاء في استجابة GraphQL نفسها
            if "errors" in result:
                print(f"❌ [Qumra GraphQL Error]: {result['errors']}")
                return None

            return result.get("data")

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
