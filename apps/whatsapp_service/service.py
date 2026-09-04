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
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# ✅ استيراد Cloudinary
import cloudinary
import cloudinary.uploader
import cloudinary.api

# ✅ استيراد النماذج من المكان الصحيح (حيث توجد الجداول فعلاً)
from apps.models.whatsapp_models import WhatsAppCustomerContact, WhatsAppMessageLog
from apps.models.supplier_db import Supplier
from apps.models.marketer_db import Marketer

# استيراد قاعدة البيانات
try:
    from apps.extensions import db
except ImportError:
    from app import db


def format_phone_number(phone: str) -> str:
    """تنسيق رقم الهاتف بشكل دولي موحد ومنطقي لضمان عدم تكرار الجهات"""
    if not phone:
        return ""
    
    # تنظيف الرقم وإزالة أي رموز غريبة ما عدا الأرقام وعلامة الزائد
    clean = "".join([c for c in str(phone) if c.isdigit() or c == '+'])
    
    if not clean.startswith('+'):
        if clean.startswith('967'):
            clean = '+' + clean
        else:
            clean = '+967' + clean.lstrip('0')
            
    # تنسيق شكل العرض للأرقام اليمنية إذا تطابق الطول
    if clean.startswith('+967') and len(clean) == 13:
        return f"{clean[:4]} {clean[4:6]} {clean[6:9]} {clean[9:]}"
        
    return clean


def clean_phone_number(phone: str) -> str:
    """تنظيف رقم الهاتف وإرجاعه بصيغة رقمية فقط مع كود الدولة"""
    if not phone:
        return ""
    # إزالة كل شيء ما عدا الأرقام
    clean = "".join(filter(str.isdigit, str(phone)))
    # إزالة الصفر في البداية
    if clean.startswith('0'):
        clean = clean[1:]
    # إضافة كود اليمن إذا كان الرقم أقل من 10 أرقام
    if len(clean) < 10:
        clean = '967' + clean
    return clean


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

    def _process_message_variables(self, text: str, contact_data: Dict[str, Any]) -> str:
        """استبدال المتغيرات في الرسالة بالبيانات الحقيقية للعميل أو التاجر أو المسوق"""
        if not contact_data:
            return text

        name = contact_data.get('name', '')
        company = contact_data.get('company', '')
        discount_code = contact_data.get('discount_code', '')
        city = contact_data.get('city', '')
        phone = contact_data.get('phone', '')

        return (
            text.replace("{name}", name)
                .replace("{company}", company)
                .replace("{discount_code}", discount_code)
                .replace("{city}", city)
                .replace("{phone}", phone)
        )

    def send_message(self, recipient_phone: str, text: str, contact_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """إرسال رسالة نصية فردية عبر Meta WhatsApp Cloud API مع حفظ كامل"""
        clean_phone = clean_phone_number(recipient_phone)

        if contact_data:
            text = self._process_message_variables(text, contact_data)

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

        # ✅ حفظ الرسالة بحالة "pending" قبل الإرسال
        try:
            msg = WhatsAppMessageLog(
                direction='outbound',
                sender_number=self.phone_number_id,
                recipient_number=clean_phone,
                content=text,
                message_type='text',
                status='pending',
                timestamp=datetime.utcnow()
            )
            db.session.add(msg)
            db.session.flush()
            msg_id = msg.id
            print(f"📝 [تم حفظ الرسالة مؤقتاً] ID: {msg_id}, To: {clean_phone}")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [خطأ حفظ الرسالة قبل الإرسال]: {e}")
            return {"status": "failed", "error": f"فشل حفظ الرسالة: {str(e)}"}

        # ✅ التحقق من التوكن
        if not self.access_token:
            try:
                msg.status = 'simulated'
                msg.wamid = f"sim_{int(datetime.utcnow().timestamp())}"
                db.session.commit()
                self._update_contact_last_message(clean_phone, text)
                print(f"📝 [محاكاة] تم إرسال رسالة إلى {clean_phone}")
                return {"status": "simulated", "message_id": msg.wamid, "to": clean_phone}
            except Exception as e:
                db.session.rollback()
                return {"status": "failed", "error": str(e)}

        # ✅ إرسال الرسالة عبر Meta API
        try:
            print(f"📤 [إرسال] إلى {clean_phone}: {text[:50]}...")
            response = requests.post(self.base_url, headers=self._get_headers(), json=payload, timeout=15)
            response_data = response.json()
            
            if response.status_code == 200:
                wamid = response_data.get('messages', [{}])[0].get('id', '')
                msg.wamid = wamid
                msg.status = 'sent'
                db.session.commit()
                self._update_contact_last_message(clean_phone, text)
                print(f"✅ [تم الإرسال] إلى {clean_phone} - WAMID: {wamid}")
                return {
                    "status": "sent",
                    "message_id": wamid,
                    "to": clean_phone,
                    "data": response_data
                }
            else:
                error_msg = response_data.get('error', {}).get('message', 'فشل الإرسال')
                error_code = response_data.get('error', {}).get('code', '')
                msg.status = 'failed'
                msg.content = f"{text} [خطأ: {error_code} - {error_msg}]"
                db.session.commit()
                print(f"❌ [فشل الإرسال] إلى {clean_phone}: {error_code} - {error_msg}")
                return {
                    "status": "failed",
                    "error": error_msg,
                    "error_code": error_code,
                    "to": clean_phone,
                    "data": response_data
                }
            
        except requests.exceptions.Timeout:
            msg.status = 'failed'
            msg.content = f"{text} [خطأ: Timeout]"
            db.session.commit()
            print(f"⏰ [مهلة] إلى {clean_phone}")
            return {"status": "failed", "error": "انتهت مهلة الاتصال بخوادم واتساب", "to": clean_phone}
            
        except Exception as e:
            msg.status = 'failed'
            msg.content = f"{text} [خطأ: {str(e)}]"
            db.session.commit()
            print(f"❌ [خطأ] إلى {clean_phone}: {str(e)}")
            return {"status": "failed", "error": str(e), "to": clean_phone}

    def send_template(
        self,
        recipient_phone: str,
        template_name: str,
        language_code: str = "ar",
        components: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """إرسال قالب رسمي معتمد من Meta"""
        clean_phone = clean_phone_number(recipient_phone)
        
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

        try:
            msg = WhatsAppMessageLog(
                direction='outbound',
                sender_number=self.phone_number_id,
                recipient_number=clean_phone,
                content=f"[قالب: {template_name}]",
                message_type='template',
                template_name=template_name,
                template_language=language_code,
                template_components=components,
                status='pending',
                timestamp=datetime.utcnow()
            )
            db.session.add(msg)
            db.session.flush()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [خطأ حفظ القالب]: {e}")

        if not self.access_token:
            return {"status": "simulated", "template": template_name, "to": clean_phone}

        try:
            response = requests.post(self.base_url, headers=self._get_headers(), json=payload, timeout=10)
            response_data = response.json()
            
            if response.status_code == 200:
                msg.status = 'sent'
                msg.wamid = response_data.get('messages', [{}])[0].get('id', '')
                db.session.commit()
            else:
                msg.status = 'failed'
                db.session.commit()
            
            return response_data
        except Exception as e:
            msg.status = 'failed'
            db.session.commit()
            return {"error": str(e), "status": "failed"}

    def send_media(self, recipient_phone: str, files: list) -> Dict[str, Any]:
        """إرسال ملفات (صور، فيديو، مستندات) عبر Meta WhatsApp Cloud API"""
        try:
            clean_phone = clean_phone_number(recipient_phone)
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
                    f"{media_type}": {
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
                
                self._record_message(
                    clean_phone, 
                    f"[{media_type}] {file.filename}", 
                    direction="outbound", 
                    media_id=media_id, 
                    status="sent" if send_res.status_code == 200 else "failed"
                )
                results.append(send_data)

            return {"status": "success", "results": results}

        except Exception as e:
            return {"error": str(e), "status": "failed"}

    def send_bulk_messages(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """إرسال رسائل جماعية مستهدفة مع استبدال المتغيرات بالبيانات الحقيقية"""
        campaign_name = campaign_data.get('campaign_name', '')
        target_category = campaign_data.get('target_category', 'all')
        message_text = campaign_data.get('message_text', '')

        target_contacts = self.get_all_contacts()

        sent_count = 0
        failed_count = 0
        for contact in target_contacts:
            if target_category != 'all' and contact.get('category') != target_category:
                continue

            personalized_message = self._process_message_variables(message_text, contact)

            result = self.send_message(contact['raw_phone'], personalized_message, contact)
            if result.get('status') in ['sent', 'simulated']:
                sent_count += 1
            else:
                failed_count += 1

        return {"success": True, "sent_count": sent_count, "failed_count": failed_count, "campaign_name": campaign_name}

    # =========================================================================
    # 2. معالجة الـ Webhook الوارد (Inbound Webhook)
    # =========================================================================

    def verify_webhook_signature(self, raw_payload: bytes, signature_header: str) -> bool:
        """التحقق الأمني من أن الطلب صادر من خوادم Meta"""
        if not self.app_secret or not signature_header:
            return False  # تصحيح الخطأ الإملائي
        
        algo, _, sig = signature_header.partition("=")
        if algo != "sha256" or not sig:
            return False  # تصحيح الخطأ الإملائي

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
                            sender_phone = clean_phone_number(msg.get("from", ""))
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
                                msg_text = "📷 صورة"
                                media_id = msg.get("image", {}).get("id", "")
                                media_url = self._get_media_url(media_id)
                            elif msg_type == "video":
                                msg_text = "🎬 فيديو"
                                media_id = msg.get("video", {}).get("id", "")
                                media_url = self._get_media_url(media_id)
                            elif msg_type == "document":
                                msg_text = "📄 ملف"
                                media_id = msg.get("document", {}).get("id", "")
                                media_url = self._get_media_url(media_id)
                            elif msg_type == "location":
                                msg_text = "📍 موقع"
                            elif msg_type == "audio":
                                msg_text = "🎵 صوت"
                                media_id = msg.get("audio", {}).get("id", "")
                            elif msg_type == "sticker":
                                msg_text = "🏷️ ملصق"
                                media_id = msg.get("sticker", {}).get("id", "")
                            else:
                                msg_text = f"نوع رسالة غير معروف: {msg_type}"

                            self._ensure_contact_exists(sender_phone, contact_profile_name, msg_text)
                            self._log_webhook_event("incoming_message", sender_phone, msg_text)
                            self._record_message(
                                sender_phone, 
                                msg_text, 
                                direction="inbound", 
                                media_id=media_id, 
                                media_url=media_url,
                                status="received"
                            )
                            print(f"📩 [رسالة واردة] من {sender_phone}: {msg_text[:50]}")

                    # 2. حالة تحديث حالة التسليم والقراءة
                    if "statuses" in value:
                        for status_update in value["statuses"]:
                            recipient_id = clean_phone_number(status_update.get("recipient_id", ""))
                            status = status_update.get("status")
                            self._update_message_status(recipient_id, status)
                            print(f"📊 [تحديث حالة] {recipient_id}: {status}")

        except Exception as e:
            self._log_webhook_event("error", "system", f"خطأ معالجة: {str(e)}")
            print(f"⚠️ [خطأ معالجة Webhook]: {e}", file=sys.stderr)

    def _update_message_status(self, phone: str, status: str) -> None:
        """تحديث حالة الرسائل المرسلة (sent, delivered, read)"""
        try:
            clean_phone = clean_phone_number(phone)
            messages = WhatsAppMessageLog.query.filter_by(
                recipient_number=clean_phone,
                direction='outbound'
            ).order_by(WhatsAppMessageLog.timestamp.desc()).limit(5).all()

            for message in messages:
                message.status = status
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [خطأ تحديث حالة الرسالة]: {e}")

    # =========================================================================
    # 3. دالة إضافة/تحديث جهة الاتصال
    # =========================================================================

    def _ensure_contact_exists(self, phone: str, name: str = "عميل واتساب", last_message: str = "") -> None:
        """إضافة جهة الاتصال تلقائياً أو تحديث آخر رسالة لها مع زيادة العداد"""
        if not phone:
            return
        clean_phone = clean_phone_number(phone)

        try:
            contact = WhatsAppCustomerContact.query.filter_by(phone=clean_phone).first()
            if not contact:
                contact = WhatsAppCustomerContact(
                    phone=clean_phone,
                    name=name if name != "عميل واتساب" else f"عميل ({clean_phone})",
                    whatsapp_profile_name=name,
                    last_message=last_message,
                    last_timestamp=datetime.utcnow(),
                    unread_count=1,
                    extra_data={"category": "customers"}
                )
                db.session.add(contact)
                print(f"👤 [جهة اتصال جديدة] {name} - {clean_phone}")
            else:
                if name and name != "عميل واتساب":
                    contact.name = name
                    contact.whatsapp_profile_name = name
                if last_message:
                    contact.last_message = last_message
                    contact.last_timestamp = datetime.utcnow()
                    contact.unread_count = (contact.unread_count or 0) + 1
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [خطأ حفظ جهة الاتصال]: {e}")

    def _update_contact_last_message(self, phone: str, message: str) -> None:
        """تحديث آخر رسالة لجهة الاتصال (للمرسلة)"""
        try:
            clean_phone = clean_phone_number(phone)
            contact = WhatsAppCustomerContact.query.filter_by(phone=clean_phone).first()
            if contact:
                contact.last_message = message
                contact.last_timestamp = datetime.utcnow()
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [خطأ تحديث جهة الاتصال]: {e}")

    # =========================================================================
    # 4. الرد الآلي
    # =========================================================================

    def _handle_smart_ai_reply(self, sender_phone: str, customer_message: str) -> None:
        """معالجة الردود الذكية باستخدام Gemini AI"""
        pass

    def _generate_gemini_reply(self, prompt: str) -> str:
        if not self.gemini_api_key:
            return "أهلاً بك في سوق محجوب أونلاين! تم استلام رسالتك وسيتواصل معك أحد ممثلي الخدمة في أقرب وقت."
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_api_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=payload, timeout=8)
            res_json = res.json()
            return res_json['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return "مرحباً بك في سوق محجوب أونلاين! نسعد بخدمتك دائماً، كيف يمكننا مساعدتك اليوم؟"

    # =========================================================================
    # 5. إدارة قواعد البيانات وسجلات المحادثات
    # =========================================================================

    def _record_message(self, phone: str, content: str, direction: str, media_id: str = "", media_url: str = "", status: str = "received") -> None:
        """تسجيل رسالة في قاعدة البيانات مع ضمان الحفظ"""
        clean_phone = clean_phone_number(phone)
        
        if direction == 'inbound':
            self._ensure_contact_exists(clean_phone, last_message=content)

        try:
            msg = WhatsAppMessageLog(
                direction=direction,
                sender_number=clean_phone if direction == 'inbound' else self.phone_number_id,
                recipient_number=self.phone_number_id if direction == 'inbound' else clean_phone,
                content=content,
                message_type='text',
                status=status,
                media_id=media_id,
                media_url=media_url,
                timestamp=datetime.utcnow()
            )
            db.session.add(msg)
            db.session.commit()
            print(f"💾 [تم حفظ الرسالة] {direction} - {clean_phone}")
        except Exception as e:
            db.session.rollback()
            print(f"⚠️ [خطأ حفظ الرسالة]: {e}")

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
        """جلب جميع جهات الاتصال ودمج الأرقام المتطابقة لمنع التكرار"""
        try:
            unique_contacts = {}

            # 1. جلب العملاء من قاعدة البيانات
            customers = WhatsAppCustomerContact.query.order_by(WhatsAppCustomerContact.last_timestamp.desc()).all()
            for c in customers:
                if not c.phone:
                    continue
                raw_phone = clean_phone_number(c.phone)
                formatted_phone = format_phone_number(raw_phone)
                extra_data = c.extra_data if isinstance(c.extra_data, dict) else {}

                unique_contacts[raw_phone] = {
                    'id': c.id,
                    'phone': formatted_phone,
                    'raw_phone': raw_phone,
                    'name': c.name or c.whatsapp_profile_name or f"عميل ({formatted_phone})",
                    'last_message': c.last_message,
                    'last_timestamp': c.last_timestamp.isoformat() if c.last_timestamp else None,
                    'unread_count': c.unread_count or 0,
                    'is_online': False,
                    'last_seen': 'آخر ظهور اليوم',
                    'category': extra_data.get('category', 'customers'),
                    'city': extra_data.get('city', ''),
                    'company': extra_data.get('company', ''),
                    'discount_code': extra_data.get('discount_code', ''),
                    'email': extra_data.get('email', ''),
                    'notes': c.notes or '',
                }

                if c.last_timestamp:
                    dt = c.last_timestamp.replace(tzinfo=None) if isinstance(c.last_timestamp, datetime) else None
                    if dt and (datetime.utcnow() - dt).total_seconds() < 300:
                        unique_contacts[raw_phone]['is_online'] = True
                        unique_contacts[raw_phone]['last_seen'] = 'متصل الآن'

            # 2. جلب التجار والموردين
            suppliers = Supplier.query.all()
            for s in suppliers:
                if not s.phone:
                    continue
                raw_phone = clean_phone_number(s.phone)
                formatted_phone = format_phone_number(raw_phone)
                
                if raw_phone in unique_contacts:
                    unique_contacts[raw_phone]['category'] = 'suppliers'
                    unique_contacts[raw_phone]['company'] = s.store_name or s.trade_name
                else:
                    unique_contacts[raw_phone] = {
                        'id': f"supplier_{s.id}",
                        'phone': formatted_phone,
                        'raw_phone': raw_phone,
                        'name': s.store_name or s.trade_name or s.owner_name or s.username,
                        'company': s.trade_name or s.store_name,
                        'city': getattr(s, 'city', ''),
                        'category': 'suppliers',
                        'unread_count': 0,
                        'is_online': False,
                        'last_seen': 'آخر ظهور اليوم',
                        'last_message': '',
                        'last_timestamp': s.created_at.isoformat() if s.created_at else None,
                    }

            # 3. جلب المسوقين
            marketers = Marketer.query.all()
            for m in marketers:
                if not m.phone:
                    continue
                raw_phone = clean_phone_number(m.phone)
                formatted_phone = format_phone_number(raw_phone)

                if raw_phone in unique_contacts:
                    unique_contacts[raw_phone]['category'] = 'marketers'
                else:
                    unique_contacts[raw_phone] = {
                        'id': f"marketer_{m.id}",
                        'phone': formatted_phone,
                        'raw_phone': raw_phone,
                        'name': m.full_name,
                        'company': '',
                        'city': '',
                        'category': 'marketers',
                        'unread_count': 0,
                        'is_online': False,
                        'last_seen': 'آخر ظهور اليوم',
                        'last_message': '',
                        'last_timestamp': m.created_at.isoformat() if m.created_at else None,
                    }

            return list(unique_contacts.values())

        except Exception as e:
            print(f"⚠️ [خطأ جلب جهات الاتصال]: {e}")
            return []

    def get_chat_history(self, phone: str) -> List[Dict[str, Any]]:
        """جلب سجل المحادثة"""
        try:
            clean_phone = clean_phone_number(phone)
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
                    'media_filename': getattr(m, 'media_filename', ''),
                }
                result.append(item)

            return result
        except Exception as e:
            print(f"⚠️ [خطأ جلب المحادثة]: {e}")
            return []

    def _get_media_url(self, media_id: str) -> str:
        try:
            if not media_id or not self.access_token:
                return ""
            url = f"https://graph.facebook.com/{self.api_version}/{media_id}"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                return res.json().get("url", "")
            return ""
        except Exception:
            return ""
