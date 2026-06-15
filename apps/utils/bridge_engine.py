# 📂 apps/utils/bridge_engine.py
import requests
import logging

# إعداد الـ Logger لتتبع أي أخطاء في الاتصال
logger = logging.getLogger(__name__)

class QumraBridgeEngine:
    def __init__(self):
        # عنوان نقطة الوصول في قمرة
        self.url = "https://mahjoub.online/admin/graphql"
        # التوكين الخاص بك (تم استخدامه هنا كمتغير ثابت)
        self.token = "qmr_e063f7f4-ed44-4c86-b105-8405326b9eb9"

    def execute_query(self, query):
        """
        محرك موحد لتنفيذ أي استعلام GraphQL.
        يستقبل الـ query كـ String ويرجع الـ JSON كـ Dictionary.
        """
        try:
            # إرسال طلب POST إلى GraphQL
            response = requests.post(
                self.url,
                headers={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json",
                },
                json={"query": query}
            )
            
            # التحقق من نجاح الطلب
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"GraphQL Error: Status Code {response.status_code} - Response: {response.text}")
                return {}
                
        except Exception as e:
            # تسجيل أي خطأ في الاتصال (مثل انقطاع الإنترنت أو خطأ في الـ URL)
            logger.error(f"Bridge Engine Connection Error: {str(e)}")
            return {}
