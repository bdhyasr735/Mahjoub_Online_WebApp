import os
from google import genai

# تهيئة عميل جوجل باستخدام المفتاح المخفي في البيئة
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

def analyze_permissions_query(prompt: str) -> str:
    try:
        # استخدام نموذج فلاش السريع والمناسب لطلبات التطبيق
        response = client.models.generate_content(
            model='gemini-2.5-flash', # أو gemini-3.6-flash حسب المتاح في مكتبتك
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"حدث خطأ أثناء معالجة الطلب: {str(e)}"
