import os
from google import genai

# تهيئة العميل باستخدام المفتاح الذي قمت بإضافته في ملف الـ .env
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def analyze_permissions_query(prompt: str) -> str:
    try:
        # استخدام النموذج السريع لمعالجة طلبات صلاحيات الموردين
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"حدث خطأ أثناء معالجة الطلب: {str(e)}"
