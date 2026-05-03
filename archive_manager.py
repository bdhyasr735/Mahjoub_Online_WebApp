import requests
import base64
import os
from urllib.parse import quote
from datetime import datetime
from config import Config

class ArchiveManager:
    def __init__(self):
        # سحب الإعدادات مع التأكد من نظافة البيانات
        self.token = Config.GITHUB_TOKEN.strip()
        self.repo = Config.GITHUB_REPO.strip()
        # المسار الأساسي للأرشيف السيادي
        self.base_url = f"https://api.github.com/repos/{self.repo}/contents/Main_Archive"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def upload_document(self, s_id, u_id, doc_type, file_data, ext=".jpg", is_txt=False):
        """
        رفع الوثائق إلى الأرشيف السحابي لـ GitHub بنظام مسارات هرمي.
        """
        try:
            now = datetime.now()
            year, month, day = now.strftime("%Y"), now.strftime("%m"), now.strftime("%d")
            # دقة زمنية عالية لمنع تكرار الأسماء (النانو ثانية)
            time_now = now.strftime("%H-%M-%S-%f") 
            
            # بناء المسار الهرمي: المعرف / السنة / الشهر / اليوم / الملف
            # نستخدم replace لمنع المشاكل في أسماء الملفات
            safe_u_id = str(u_id).replace(" ", "_")
            path = f"{s_id}/{year}/{month}/{day}/{safe_u_id}_{doc_type}_{time_now}{ext}"
            url = f"{self.base_url}/{quote(path)}"
            
            # تجهيز المحتوى
            if is_txt:
                content_bytes = str(file_data).encode('utf-8')
            else:
                # التأكد أن البيانات بتنسيق bytes
                content_bytes = file_data if isinstance(file_data, bytes) else file_data.read()

            content_base64 = base64.b64encode(content_bytes).decode('utf-8')
            
            payload = {
                "message": f"🛡️ Archiving System - Supplier: {s_id} - Ref: {u_id}",
                "content": content_base64,
                "branch": "main"
            }
            
            response = requests.put(url, json=payload, headers=self.headers, timeout=30)
            
            if response.status_code in [200, 201]:
                print(f"✅ تم الأرشفة بنجاح في المسار: {path}")
                return path
            else:
                print(f"⚠️ فشل الأرشفة. رمز الحالة: {response.status_code} - الرسالة: {response.text}")
                return None
                
        except Exception as e: 
            print(f"❌ خطأ فني فادح في الأرشفة: {str(e)}")
            return None

    def delete_temporary_file(self, github_path):
        """
        المشرط الجراحي: حذف الملفات المؤقتة بعد انتهاء الحاجة إليها (مثل صور المنتجات).
        """
        if not github_path:
            return False
            
        try:
            url = f"{self.base_url}/{quote(github_path)}"
            # 1. جلب بصمة SHA للملف (إلزامي للحذف في GitHub)
            get_res = requests.get(url, headers=self.headers, timeout=20)
            
            if get_res.status_code == 200:
                file_sha = get_res.json().get('sha')
                
                # 2. تنفيذ الحذف النهائي
                payload = {
                    "message": f"♻️ Auto-Cleanup: Purging temporary file {github_path}",
                    "sha": file_sha,
                    "branch": "main"
                }
                del_res = requests.delete(url, json=payload, headers=self.headers, timeout=20)
                
                if del_res.status_code == 200:
                    print(f"✅ تم تنظيف الأرشيف من الملف: {github_path}")
                    return True
            return False
        except Exception as e:
            print(f"❌ خطأ أثناء عملية التنظيف الجراحي: {e}")
            return False

    def upload_full_package(self, data, files):
        """
        أرشفة الحزمة الكاملة للمورد (بيانات نصية + ملفات ثبوتية).
        """
        # استخراج المعرف الفريد للمورد
        s_id = data.get('supplier_id') or data.get('vendor_uid') or "GENERIC_ID"
        
        # 1. توليد ورفع السجل النصي السيادي
        profile_content = self._generate_text_log(data)
        self.upload_document(s_id, "SYSTEM", "LOG", profile_content, ".txt", True)
        
        # 2. رفع المرفقات الثبوتية
        for i, file in enumerate(files, start=1):
            if file and file.filename:
                # استخراج الامتداد الأصلي للملف
                ext = os.path.splitext(file.filename)[1].lower() or ".jpg"
                file_bytes = file.read()
                
                if file_bytes:
                    self.upload_document(s_id, f"DOC_{i}", "Identity", file_bytes, ext)
                
                # إعادة مؤشر القراءة للبداية في حال احتجنا للملف مرة أخرى في الكود
                file.seek(0)

    def _generate_text_log(self, d):
        """
        توليد صياغة السجل الرسمي للمورد.
        """
        return f"""
============================================================
           🛡️ السجل الرسمي لنظام محجوب أونلاين 🛡️
============================================================
تاريخ الأرشفة: {datetime.now().strftime('%Y-%m-%d | %H:%M:%S')}
معرف المورد (ID): {d.get('supplier_id', 'N/A')}
------------------------------------------------------------
تفاصيل الحساب:
- اسم المستخدم: {d.get('username', 'غير محدد')}
- الاسم الكامل: {d.get('full_name', 'غير محدد')}
- هاتف التواصل: {d.get('phone', 'غير محدد')}

الموقع الإداري:
- المحافظة: {d.get('province', 'غير محدد')}
- المديرية: {d.get('district', 'غير محدد')}

البيانات المالية:
- البنك المعتمد: {d.get('bank_name', 'غير محدد')}
- رقم الحساب: {d.get('bank_acc', 'غير محدد')}
------------------------------------------------------------
حالة الحوكمة: مؤرشف بنجاح تحت نظام القيادة المركزية.
============================================================
"""
