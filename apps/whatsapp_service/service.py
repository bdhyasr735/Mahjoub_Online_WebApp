# -*- coding: utf-8 -*-
# 📂 apps/whatsapp_service/service.py
"""
سوق محجوب أونلاين - خدمة الواتساب ومحرك الذكاء الاصطناعي
WhatsApp Service for Meta Cloud API v26.0 & Gemini AI
"""

import os
import json
import hmac
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# ✅ استيراد Cloudinary
import cloudinary
import cloudinary.uploader
import cloudinary.api

# ✅ استيراد النماذج من المكان الصحيح (حيث توجد الجداول فعلاً)
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog
from apps.extensions import db

class WhatsAppService:
    def __init__(self):
        # إعدادات الربط مع Meta Cloud API v26.0 (آمن - تقرأ من Railway فقط)
        self.api_version = os.getenv("WHATSAPP_API_VERSION", "v26.0")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
        self.waba_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
        self.verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN", "")
        self.app_secret = os.getenv("WHATSAPP_APP_SECRET", "")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

        # ✅ إعداد Cloudinary
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
            api_key=os.getenv("CLOUDINARY_API_KEY", ""),
            api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
            secure=True
        )

        # روابط Meta Graph API
        self.base_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/messages"
        self.media_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/media"

        # مخزن مؤقت للمحادثات وسجلات الويب هوك
        self.webhook_logs: List[Dict[str, Any]] = []
        self.contacts_db: Dict[str, Dict[str, Any]] = {}
        self.messages_db: Dict[str, List[Dict[str, Any]]] = {}

    # =========================================================================
    # 1. إرسال الرسائل والقوالب والوسائط (Outbound Meta API)
    # =========================================================================

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def send_message(self, recipient_phone: str, text: str) -> Dict[str, Any]:
        """إرسال رسالة نصية فردية عبر Meta WhatsApp Cloud API"""
        clean_phone = recipient_phone.replace("+", "").replace(" ", "").strip()
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": clean_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": text
            }
        }

        # حفظ الرسالة محلياً (outbound لا يزيد unread_count)
        self._record_message(clean_phone, text, direction="outbound", status="sent")

        if not self.access_token:
            return {"status": "simulated", "message_id": f"sim_{int(datetime.utcnow().timestamp())}", "to": clean_phone}

        try:
            response = requests.post(self.base_url, headers=self._get_headers(), json=payload, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    def send_template(
        self,
        recipient_phone: str,
        template_name: str,
        language_code: str = "ar",
        components: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """إرسال قالب رسمي معتمد من Meta"""
        clean_phone = recipient_phone.replace("+", "").replace(" ", "").strip()
        payload = {
            "messaging_product": "whatsapp",
            "to": clean_phone,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
                "components": components or []
            }
        }

        self._record_message(clean_phone, f"[قالب رسمي: {template_name}]", direction="outbound", status="sent")

        if not self.access_token:
            return {"status": "simulated", "template": template_name, "to": clean_phone}

        try:
            response = requests.post(self.base_url, headers=self._get_headers(), json=payload, timeout=10)
            return response.json()
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    def send_media(self, recipient_phone: str, files: list) -> Dict[str, Any]:
        """إرسال ملفات (صور، فيديو، مستندات) عبر Meta WhatsApp Cloud API"""
        try:
            clean_phone = recipient_phone.replace("+", "").replace(" ", "").strip()
            results = []
            
            for file in files:
                if not file:
                    continue
                    
                file_type = file.content_type
                if file_type.startswith('image/'):
                    media_type = 'image'
                elif file_type.startswith('video/'):
                    media_type = 'video'
                else:
                    media_type = 'document'
                
                upload_url = f"https://graph.facebook.com/{self.api_version}/{self.phone_number_id}/media"
                upload_res = requests.post(
                    upload_url,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    files={
                        "file": (file.filename, file.stream, file.content_type),
                        "type": (None, media_type),
                        "messaging_product": (None, "whatsapp")
                    },
                    timeout=30
                )
                upload_data = upload_res.json()
                
                if "id" not in upload_data:
                    return {"status": "failed", "error": upload_data.get("error", {}).get("message", "فشل رفع الملف")}
                
                media_id = upload_data["id"]
                
                payload = {
                    "messaging_product": "whatsapp",
                    "to": clean_phone,
                    "type": media_type,
                    "media_type": {
                        "id": media_id
                    }
                }
                
                send_res = requests.post(
                    self.base_url,
                    headers=self._get_headers(),
                    json=payload,
                    timeout=10
                )
                
                send_data = send_res.json()
                self._record_message(clean_phone, f"[{media_type}] ملف مرفق", direction="outbound", media_id=media_id, status="sent")
                results.append(send_data)
            
            return {"status": "success", "results": results}
            
        except Exception as e:
            return {"error": str(e), "status": "failed"}

    # =========================================================================
    # 2. معالجة الـ Webhook الوارد (Inbound Webhook)
    # =========================================================================

    def verify_webhook_signature(self, raw_payload: bytes, signature_header: str) -> bool:
        """التحقق الأمني من أن الطلب صادر من خوادم Meta"""
        if not self.app_secret or not signature_header:
            return True
        expected_hash = hmac.new(
            self.app_secret.encode('utf-8'),
            raw_payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected_hash}", signature_header)

    def process_incoming_payload(self, data: Dict[str, Any]) -> None:
        """تحليل ومعالجة الرسائل والأحداث الواردة من Meta Webhook"""
        try:
            entries = data.get("entry", [])
            for entry in entries:
                changes = entry.get("changes", [])
                for change in changes:
                    value = change.get("value", {})
                    
                    contact_profile_name = "عميل محجوب"
                    if "contacts" in value and len(value["contacts"]) > 0:
                        contact_profile_name = value["contacts"][0].get("profile", {}).get("name", "عميل محجوب")

                    # 1. حالة وصول رسالة جديدة من عميل
                    if "messages" in value:
                        for msg in value["messages"]:
                            sender_phone = str(msg.get("from", "")).replace("+", "").strip()
                            msg_type = msg.get("type")
                            msg_text = ""
                            media_id = ""
                            media_url = ""

                            if msg_type == "text":
                                msg_text = msg.get("text", {}).get("body", "")
                            elif msg_type == "button":
                                msg_text = msg.get("button", {}).get("text", "")
                            elif msg_type == "interactive":
                                msg_text = msg.get("interactive", {}).get("button_reply", {}).get("title", "")
                            elif msg_type == "image":
                                msg_text = "صورة"
                                media_id = msg.get("image", {}).get("id", "")
                                media_url = self._get_media_url(media_id)
                                if media_url:
                                    try:
                                        response = requests.get(media_url, timeout=30)
                                        if response.status_code == 200:
                                            temp_file = f"temp_{media_id}.jpg"
                                            with open(temp_file, "wb") as f:
                                                f.write(response.content)
                                            permanent_url = self._upload_to_cloudinary(temp_file, media_id)
                                            if permanent_url:
                                                media_url = permanent_url
                                            if os.path.exists(temp_file):
                                                os.remove(temp_file)
                                    except Exception as e:
                                        print(f"⚠️ [خطأ تحميل صورة من Meta]: {e}")
                            elif msg_type == "video":
                                msg_text = "فيديو"
                                media_id = msg.get("video", {}).get("id", "")
                                media_url = self._get_media_url(media_id)
                            elif msg_type == "document":
                                msg_text = "ملف مرفق"
                                media_id = msg.get("document", {}).get("id", "")
                                media_url = self._get_media_url(media_id)
                            elif msg_type == "location":
                                msg_text = "موقع جغرافي"

                            # ✅ تسجيل جهة الاتصال (هنا يتم زيادة unread_count)
                            self._ensure_contact_exists(sender_phone, contact_profile_name, msg_text)
                            self._log_webhook_event("incoming_message", sender_phone, msg_text)
                            
                            # ✅ تسجيل الرسالة كـ inbound (هنا أيضاً يتم زيادة unread_count)
                            self._record_message(sender_phone, msg_text, direction="inbound", media_id=media_id, media_url=media_url)

                            # ❌ تم تعطيل الرد الآلي
                            # self._handle_smart_ai_reply(sender_phone, msg_text)

                    # 2. حالة تحديث حالة التسليم والقراءة
                    if "statuses" in value:
                        for status_update in value["statuses"]:
                            recipient_id = str(status_update.get("recipient_id", "")).replace("+", "").strip()
                            status = status_update.get("status")
                            self._update_message_status(recipient_id, status)

        except Exception as e:
            self._log_webhook_event("error", "system", f"خطأ معالجة: {str(e)}")

    def _update_message_status(self, phone: str, status: str) -> None:
        """تحديث حالة الرسائل المرسلة (sent, delivered, read)"""
        try:
            message = WhatsAppMessageLog.query.filter_by(
                recipient_number=phone,
                direction='outbound'
            ).order_by(WhatsAppMessageLog.timestamp.desc()).first()
            
            if message:
                message.status = status
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [خطأ تحديث حالة الرسالة]: {e}")

    # =========================================================================
    # 3. ✅ دالة إضافة/تحديث جهة الاتصال (مع زيادة unread_count)
    # =========================================================================

    def _ensure_contact_exists(self, phone: str, name: str = "عميل واتساب", last_message: str = "") -> None:
        """إضافة جهة الاتصال تلقائياً أو تحديث آخر رسالة لها مع زيادة العداد"""
        if not phone:
            return
        phone = phone.replace("+", "").strip()
        
        # ✅ الحفظ في قاعدة البيانات
        try:
            contact = WhatsAppCustomerContact.query.filter_by(phone=phone).first()
            if not contact:
                contact = WhatsAppCustomerContact(
                    phone=phone,
                    name=name if name != "عميل واتساب" else f"عميل (+{phone})",
                    whatsapp_profile_name=name,
                    last_message=last_message,
                    last_timestamp=datetime.utcnow(),
                    unread_count=1  # ✅ أول رسالة = 1
                )
                db.session.add(contact)
            else:
                # ✅ تحديث بيانات جهة الاتصال الموجودة
                if name and name != "عميل واتساب":
                    contact.name = name
                    contact.whatsapp_profile_name = name
                if last_message:
                    contact.last_message = last_message
                    contact.last_timestamp = datetime.utcnow()
                    # ✅ ✅ ✅ زيادة عداد الرسائل غير المقروءة (المهم!)
                    contact.unread_count = (contact.unread_count or 0) + 1
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [خطأ حفظ جهة الاتصال في الجدول]: {e}")
        
        # ✅ الحفظ في الذاكرة (القاموس)
        if phone not in self.contacts_db:
            self.contacts_db[phone] = {
                "phone": phone,
                "name": name if name != "عميل واتساب" else f"عميل (+{phone})",
                "last_message": last_message,
                "last_message_time": datetime.utcnow().strftime("%H:%M"),
                "unread_count": 1
            }
        else:
            if name and name != "عميل واتساب":
                self.contacts_db[phone]["name"] = name
            if last_message:
                self.contacts_db[phone]["last_message"] = last_message
                self.contacts_db[phone]["last_message_time"] = datetime.utcnow().strftime("%H:%M")
                # ✅ ✅ ✅ زيادة العداد في الذاكرة أيضاً
                self.contacts_db[phone]["unread_count"] = (self.contacts_db[phone].get("unread_count", 0) or 0) + 1

    # =========================================================================
    # 4. ❌ تم تعطيل الرد الآلي
    # =========================================================================

    def _handle_smart_ai_reply(self, sender_phone: str, customer_message: str) -> None:
        """❌ تم تعطيل الرد الآلي بناءً على طلب العميل"""
        # تم إيقاف الرد الآلي - لا يتم إرسال أي ردود تلقائية
        return
        
        # الكود التالي لن يتم تنفيذه أبداً
        if not self.gemini_api_key:
            return
        
        prompt = (
            "أنت المساعد الذكي الرسمي لخدمة عملاء 'سوق محجوب أونلاين'. "
            "أجب بأسلوب تجاري راقٍ وموجز وودود، واستفسر عما إذا كان العميل بحاجة للمساعدة "
            "في إتمام طلبه أو الاستعلام عن الشحنات والأسعار.\n"
            f"رسالة العميل: {customer_message}"
        )
        
        reply_text = self._generate_gemini_reply(prompt)
        if reply_text:
            self.send_message(sender_phone, reply_text)

    def _generate_gemini_reply(self, prompt: str) -> str:
        """استدعاء نموذج Gemini AI لتوليد الردود الفورية"""
        if not self.gemini_api_key:
            return "أهلاً بك في سوق محجوب أونلاين! تم استلام رسالتك وسيتواصل معك أحد ممثلي الخدمة في أقرب وقت."

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            res = requests.post(url, json=payload, timeout=8)
            res_json = res.json()
            return res_json['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return "مرحباً بك في سوق محجوب أونلاين! نسعد بخدمتك دائماً، كيف يمكننا مساعدتك اليوم؟"

    # =========================================================================
    # 5. إدارة قواعد البيانات وسجلات المحادثات
    # =========================================================================

    def _record_message(self, phone: str, content: str, direction: str, media_id: str = "", media_url: str = "", status: str = "received") -> None:
        clean_phone = phone.replace("+", "").strip()
        
        # ✅ نمرر last_message فقط، وزيادة unread_count ستتم داخل _ensure_contact_exists
        self._ensure_contact_exists(clean_phone, last_message=content)
        
        # ✅ الحفظ في قاعدة البيانات
        try:
            msg = WhatsAppMessageLog(
                direction=direction,
                sender_number=clean_phone if direction == 'inbound' else '967784439991',
                recipient_number='967784439991' if direction == 'inbound' else clean_phone,
                content=content,
                message_type='text',
                status=status,
                media_id=media_id,
                media_url=media_url
            )
            db.session.add(msg)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [خطأ حفظ الرسالة في الجدول]: {e}")
        
        # ✅ الحفظ في الذاكرة (القاموس)
        if clean_phone not in self.messages_db:
            self.messages_db[clean_phone] = []
        self.messages_db[clean_phone].append({
            "id": f"msg_{int(datetime.utcnow().timestamp() * 1000)}",
            "direction": direction,
            "content": content,
            "media_id": media_id,
            "media_url": media_url,
            "status": status,
            "timestamp": datetime.utcnow().strftime("%H:%M")
        })

    def _log_webhook_event(self, event_type: str, phone: str, status: str) -> None:
        self.webhook_logs.insert(0, {
            "timestamp": datetime.utcnow().strftime("%H:%M:%S"),
            "event_type": event_type,
            "phone": phone,
            "status": status
        })
        if len(self.webhook_logs) > 100:
            self.webhook_logs.pop()

    # =========================================================================
    # 6. دوال جلب البيانات
    # =========================================================================

    def get_all_contacts(self) -> List[Dict[str, Any]]:
        """جلب قائمة جهات الاتصال (من قاعدة البيانات أولاً)"""
        try:
            contacts = WhatsAppCustomerContact.query.order_by(WhatsAppCustomerContact.last_timestamp.desc()).all()
            
            result = []
            for c in contacts:
                data = {
                    'phone': c.phone,
                    'name': c.name or c.whatsapp_profile_name or f"عميل ({c.phone})",
                    'last_message': c.last_message,
                    'last_timestamp': c.last_timestamp.isoformat() if c.last_timestamp else None,
                    'unread_count': c.unread_count or 0,
                    'is_online': False,
                    'last_seen': 'آخر ظهور اليوم'
                }
                if c.last_timestamp:
                    if isinstance(c.last_timestamp, datetime):
                        c.last_timestamp = c.last_timestamp.replace(tzinfo=None)
                        time_diff = datetime.utcnow() - c.last_timestamp
                        if time_diff.total_seconds() < 300:
                            data['is_online'] = True
                            data['last_seen'] = 'متصل الآن'
                        else:
                            data['is_online'] = False
                            if c.last_timestamp.date() == datetime.utcnow().date():
                                data['last_seen'] = f"آخر ظهور اليوم {c.last_timestamp.strftime('%H:%M')}"
                            elif c.last_timestamp.date() == (datetime.utcnow() - timedelta(days=1)).date():
                                data['last_seen'] = f"آخر ظهور أمس {c.last_timestamp.strftime('%H:%M')}"
                            else:
                                data['last_seen'] = f"آخر ظهور {c.last_timestamp.strftime('%d/%m/%Y %H:%M')}"
                result.append(data)
            
            return result
        except Exception as e:
            print(f"⚠️ [خطأ جلب جهات الاتصال من الجداول]: {e}")
            return list(self.contacts_db.values())

    def get_chat_history(self, phone: str) -> List[Dict[str, Any]]:
        """جلب سجل المحادثة (من قاعدة البيانات أولاً)"""
        try:
            clean_phone = phone.replace("+", "").strip()
            messages = WhatsAppMessageLog.query.filter(
                (WhatsAppMessageLog.sender_number == clean_phone) |
                (WhatsAppMessageLog.recipient_number == clean_phone)
            ).order_by(WhatsAppMessageLog.timestamp.asc()).all()
            
            result = []
            for m in messages:
                item = {
                    'id': m.id,
                    'direction': m.direction,
                    'content': m.content,
                    'status': m.status,
                    'timestamp': m.timestamp.strftime("%H:%M") if m.timestamp else '',
                    'media_url': m.media_url,
                    'media_type': m.message_type,
                    'media_filename': m.media_filename,
                }
                result.append(item)
            
            return result
        except Exception as e:
            print(f"⚠️ [خطأ جلب المحادثة من الجداول]: {e}")
            return self.messages_db.get(phone.replace("+", "").strip(), [])

    def _get_media_url(self, media_id: str) -> str:
        """الحصول على رابط مؤقت للوسائط من Meta"""
        try:
            url = f"https://graph.facebook.com/{self.api_version}/{media_id}"
            res = requests.get(
                url,
                headers={"Authorization": f"Bearer {self.access_token}"},
                timeout=10
            )
            data = res.json()
            return data.get("url", "")
        except Exception:
            return ""

    def _upload_to_cloudinary(self, file_path: str, public_id: str) -> str:
        """رفع ملف إلى Cloudinary وإرجاع الرابط الدائم"""
        try:
            upload_result = cloudinary.uploader.upload(
                file_path,
                public_id=public_id,
                folder=f"whatsapp/{public_id.split('_')[0]}"
            )
            return upload_result.get("secure_url", "")
        except Exception as e:
            print(f"⚠️ [خطأ رفع إلى Cloudinary]: {e}")
            return ""

    # =========================================================================
    # 7. دوال إضافية
    # =========================================================================

    def get_webhook_logs(self) -> List[Dict[str, Any]]:
        return self.webhook_logs

    def get_approved_templates(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "mahjoob_order_confirmation",
                "category": "خدمات وطلبات (Utility)",
                "language": "ar",
                "status": "APPROVED",
                "body_text": "مرحباً {{1}}، تم تأكيد طلبك رقم #{{2}} بقيمة {{3}} ر.س من سوق محجوب أونلاين بنجاح. سنوافيك برابط التتبع فور انطلاق الشحنة."
            },
            {
                "name": "mahjoob_shipping_update",
                "category": "الشحن والتوصيل (Utility)",
                "language": "ar",
                "status": "APPROVED",
                "body_text": "أهلاً {{1}}، شحنتك رقم #{{2}} خرجت للتوصيل الآن مع شركة الشحن. رقم البوليصة: {{3}}."
            },
            {
                "name": "mahjoob_merchant_alert",
                "category": "تنبيهات التجار (Alert)",
                "language": "ar",
                "status": "APPROVED",
                "body_text": "عزيزي التاجر {{1}}، ورد طلب جملة جديد رقم #{{2}} على منتجاتك. يرجى تجهيز الشحنة."
            }
        ]

    def get_current_config(self) -> Dict[str, Any]:
        return {
            "whatsapp_phone_number_id": self.phone_number_id,
            "whatsapp_business_account_id": self.waba_id,
            "whatsapp_access_token": self.access_token,
            "whatsapp_verify_token": self.verify_token,
            "whatsapp_api_version": self.api_version
        }

    def update_config(self, new_config: Dict[str, Any]) -> None:
        self.phone_number_id = new_config.get("whatsapp_phone_number_id", self.phone_number_id)
        self.waba_id = new_config.get("whatsapp_business_account_id", self.waba_id)
        self.access_token = new_config.get("whatsapp_access_token", self.access_token)
        self.verify_token = new_config.get("whatsapp_verify_token", self.verify_token)

    def clear_demo_data(self) -> Dict[str, Any]:
        """تفريغ كافة البيانات الوهمية والمحادثات"""
        self.contacts_db.clear()
        self.messages_db.clear()
        self.webhook_logs.clear()
        return {"success": True, "message": "تم تفريغ كافة البيانات التجريبية بنجاح."}

    # =========================================================================
    # 8. دالة تعديل اسم العميل
    # =========================================================================

    def update_contact_name(self, phone: str, name: str) -> Dict[str, Any]:
        """تعديل اسم جهة اتصال في قاعدة البيانات"""
        try:
            clean_phone = phone.replace("+", "").strip()
            contact = WhatsAppCustomerContact.query.filter_by(phone=clean_phone).first()
            
            if not contact:
                return {"error": "Contact not found", "status": "failed"}
            
            contact.name = name
            contact.whatsapp_profile_name = name
            db.session.commit()
            
            if clean_phone in self.contacts_db:
                self.contacts_db[clean_phone]["name"] = name
            
            return {"success": True, "message": "تم تعديل الاسم بنجاح", "name": name}
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "failed"}

    # =========================================================================
    # 9. دالة تصفير عداد الرسائل غير المقروءة
    # =========================================================================

    def mark_contact_as_read(self, phone: str) -> Dict[str, Any]:
        """تصفير عداد الرسائل غير المقروءة عند فتح المحادثة"""
        try:
            clean_phone = phone.replace("+", "").strip()
            contact = WhatsAppCustomerContact.query.filter_by(phone=clean_phone).first()
            
            if contact:
                contact.unread_count = 0
                db.session.commit()
                # تحديث في الذاكرة أيضاً
                if clean_phone in self.contacts_db:
                    self.contacts_db[clean_phone]["unread_count"] = 0
                return {"success": True, "message": "تم تصفير العداد"}
            return {"success": False, "message": "العميل غير موجود"}
        except Exception as e:
            db.session.rollback()
            return {"error": str(e), "status": "failed"}
