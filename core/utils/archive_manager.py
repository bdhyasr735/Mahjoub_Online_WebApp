import os
import requests
import base64
from datetime import datetime
from flask import current_app

class ArchiveManager:
    """
    مدير الأرشفة السيادية - منظومة محجوب أونلاين v3.6
    وظيفة المحرك: نقل الأصول والوثائق إلى مستودع Sovereign Assets المستقل
    """

    def __init__(self):
        # قراءة المفتاح السيادي من متغيرات بيئة Railway
        self.token = os.getenv('SOVEREIGN_ASSETS_TOKEN')
        self.repo_owner = "alimohm"
        self.repo_name = "Mahjoub-Sovereign-Assets"
        self.api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/contents/"

    def _get_headers(self):
        return {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def generate_path(self, entity_id, folder_name="الوثائق_والتأريخ"):
        """
        توليد المسار الهرمي: ID / Year / Month / Day / Folder
        """
        now = datetime.now()
        path = f"{entity_id}/{now.year}/{now.month:02d}/{now.day:02d}/{folder_name}"
        return path

    def archive_file(self, file_data, filename, entity_id, folder_name="الوثائق_والتأريخ", commit_type="Archiving"):
        """
        المحرك الرئيسي لرفع الملفات (صور، سندات، أو سجلات) إلى GitHub
        """
        if not self.token:
            print("خطأ سيادي: مفتاح الوصول (Token) غير معرف في النظام!")
            return False

        # 1. بناء المسار الكامل للملف في المستودع
        target_path = f"{self.generate_path(entity_id, folder_name)}/{filename}"
        url = self.api_url + target_path

        # 2. تشفير الملف بصيغة Base64 (متطلب GitHub API)
        if hasattr(file_data, 'read'):
            encoded_content = base64.b64encode(file_data.read()).decode('utf-8')
        else:
            encoded_content = base64.b64encode(file_data).decode('utf-8')

        # 3. إعداد رسالة الالتزام (Commit Message) حسب البروتوكول المطلوب
        commit_message = f"{commit_type} - ID: {entity_id} - Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}"

        payload = {
            "message": commit_message,
            "content": encoded_content
        }

        # 4. تنفيذ عملية الرفع عبر API
        try:
            response = requests.put(url, json=payload, headers=self._get_headers())
            if response.status_code in [201, 200]:
                print(f"تمت الأرشفة بنجاح: {target_path}")
                return response.json()['content']['download_url']
            else:
                print(f"فشل الأرشفة: {response.json().get('message')}")
                return False
        except Exception as e:
            print(f"خطأ في محرك الأرشفة: {str(e)}")
            return False

    def archive_data_as_json(self, data_dict, filename, entity_id, folder_name="اليومية"):
        """
        أرشفة البيانات (سندات، نماذج تسجيل) كملف نصي/JSON للتوثيق التاريخي
        """
        import json
        json_data = json.dumps(data_dict, indent=4, ensure_ascii=False)
        return self.archive_file(
            json_data.encode('utf-8'), 
            f"{filename}.json", 
            entity_id, 
            folder_name, 
            commit_type="Data Archive"
        )

# إنشاء نسخة مفردة من المدير لاستخدامها في النظام
archive_sys = ArchiveManager()
